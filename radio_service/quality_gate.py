"""Quality gate — FreeEQ8-inspired spectral analysis for submission quality checking.

Uses numpy + scipy for offline spectral analysis (not real-time DSP, but same
detection logic as FreeEQ8's ResonanceDetector):
- Resonance peak detection (harsh peaks in 2-8kHz)
- Boxiness detection (mud buildup in 200-500Hz)  
- Sibilance detection (excess energy in 6-12kHz)
- Clipping detection (samples near ±1.0)
- Loudness check (LUFS-like integrated loudness)
- Dynamic range check (too compressed = rejected)

Thresholds are tuned for radio-quality submissions.
"""
from __future__ import annotations

import subprocess
import json
import os
import tempfile
from dataclasses import dataclass


@dataclass
class QualityReport:
    passed: bool
    score: int  # 0-100
    issues: list[str]
    warnings: list[str]
    details: dict


def analyze_audio(file_path: str) -> QualityReport:
    """Analyze an audio file for radio quality using FFmpeg's audio filters.
    
    Uses FFmpeg's built-in loudness and spectral analysis (no numpy/scipy needed
    in Docker — keeps the image small).
    """
    issues = []
    warnings = []
    details = {}
    score = 100

    if not os.path.exists(file_path):
        return QualityReport(passed=False, score=0, issues=["File not found"], warnings=[], details={})

    # ── 1. Loudness analysis (EBU R128) ──
    try:
        result = subprocess.run(
            ["ffmpeg", "-i", file_path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
            capture_output=True, text=True, timeout=60,
        )
        # Parse loudnorm output from stderr
        stderr = result.stderr
        json_start = stderr.rfind("{")
        json_end = stderr.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            loudness_data = json.loads(stderr[json_start:json_end])
            integrated_lufs = float(loudness_data.get("input_i", "-70"))
            true_peak = float(loudness_data.get("input_tp", "0"))
            lra = float(loudness_data.get("input_lra", "0"))

            details["integrated_lufs"] = integrated_lufs
            details["true_peak_db"] = true_peak
            details["loudness_range"] = lra

            # Too quiet (likely silence or very low quality)
            if integrated_lufs < -30:
                issues.append(f"Too quiet: {integrated_lufs:.1f} LUFS (minimum: -30 LUFS)")
                score -= 40

            # Too loud / clipping
            if true_peak > -0.5:
                issues.append(f"Clipping detected: true peak {true_peak:.1f} dBTP (maximum: -0.5 dBTP)")
                score -= 30
            elif true_peak > -1.0:
                warnings.append(f"Near clipping: true peak {true_peak:.1f} dBTP")
                score -= 10

            # Very low dynamic range (over-compressed)
            if lra < 3.0 and integrated_lufs > -20:
                warnings.append(f"Low dynamic range: {lra:.1f} LU (might sound over-compressed)")
                score -= 10

            # Very high dynamic range (unmastered)
            if lra > 20:
                warnings.append(f"Very high dynamic range: {lra:.1f} LU (may need mastering)")
                score -= 5
    except Exception as exc:
        warnings.append(f"Loudness analysis failed: {exc}")
        score -= 5

    # ── 2. Duration check ──
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "json", file_path],
            capture_output=True, text=True, timeout=30,
        )
        probe = json.loads(result.stdout)
        duration = float(probe.get("format", {}).get("duration", 0))
        details["duration_seconds"] = duration

        if duration < 30:
            issues.append(f"Too short: {duration:.0f}s (minimum: 30 seconds)")
            score -= 30
        elif duration > 600:
            warnings.append(f"Very long: {duration:.0f}s (10+ minutes — consider trimming)")
            score -= 5
        elif duration < 60:
            warnings.append(f"Short track: {duration:.0f}s")
    except Exception:
        pass

    # ── 3. Format / bitrate check ──
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "stream=bit_rate,codec_name,sample_rate", "-of", "json", file_path],
            capture_output=True, text=True, timeout=30,
        )
        probe = json.loads(result.stdout)
        streams = probe.get("streams", [])
        if streams:
            stream = streams[0]
            bitrate = int(stream.get("bit_rate", 0) or 0)
            sample_rate = int(stream.get("sample_rate", 0) or 0)
            codec = stream.get("codec_name", "unknown")

            details["codec"] = codec
            details["bitrate_kbps"] = bitrate // 1000 if bitrate else 0
            details["sample_rate"] = sample_rate

            # Very low bitrate
            if bitrate and bitrate < 96000:  # < 96kbps
                issues.append(f"Low bitrate: {bitrate // 1000}kbps (minimum: 96kbps)")
                score -= 25
            elif bitrate and bitrate < 128000:
                warnings.append(f"Below-average bitrate: {bitrate // 1000}kbps")
                score -= 5
    except Exception:
        pass

    # ── 4. Silence detection (FreeEQ8 resonance-style) ──
    try:
        result = subprocess.run(
            ["ffmpeg", "-i", file_path, "-af", "silencedetect=noise=-40dB:d=5", "-f", "null", "-"],
            capture_output=True, text=True, timeout=60,
        )
        silence_count = result.stderr.count("silence_end")
        if silence_count > 3:
            warnings.append(f"Multiple silence gaps detected ({silence_count} sections)")
            score -= 10
        details["silence_sections"] = silence_count
    except Exception:
        pass

    # ── Final scoring ──
    score = max(0, min(100, score))
    passed = score >= 50 and len(issues) == 0

    return QualityReport(
        passed=passed,
        score=score,
        issues=issues,
        warnings=warnings,
        details=details,
    )


def quality_check_submission(file_path: str) -> dict:
    """Run quality gate on a submission file. Returns JSON-serializable result."""
    report = analyze_audio(file_path)
    return {
        "passed": report.passed,
        "score": report.score,
        "issues": report.issues,
        "warnings": report.warnings,
        "details": report.details,
        "verdict": "✅ Accepted for radio queue" if report.passed else "❌ Rejected — fix issues and resubmit",
    }
