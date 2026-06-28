#!/usr/bin/env python3
"""TizWildin 24/7 Radio Stream — FFmpeg RTMP to YouTube.

Flow:
1. Bootstrap: download tracks from SoundCloud playlist (if MUSIC_DIR is empty)
2. Loop forever:
   a. Pick next track (submissions priority > shuffled playlist)
   b. Generate Now Playing overlay image
   c. Stream audio + overlay via FFmpeg to YouTube RTMP
   d. On track end, loop to next
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from config import (
    AUDIO_BITRATE, FRAMERATE, MUSIC_DIR, OVERLAY_OUTPUT, PRESET,
    STREAM_HEIGHT, STREAM_WIDTH, VIDEO_BITRATE, YOUTUBE_RTMP_KEY, YOUTUBE_RTMP_URL,
)
from overlay import generate_default_background, generate_overlay
from queue_manager import RadioQueue, bootstrap_from_soundcloud, scan_local_files


def build_ffmpeg_command(audio_path: str, overlay_path: str) -> list[str]:
    """Build the FFmpeg command to stream one track to YouTube RTMP."""
    rtmp_url = f"{YOUTUBE_RTMP_URL}/{YOUTUBE_RTMP_KEY}"
    return [
        "ffmpeg",
        "-re",                          # Read input at native framerate
        "-loop", "1",                   # Loop the overlay image
        "-i", overlay_path,             # Video input (static image)
        "-i", audio_path,               # Audio input
        "-c:v", "libx264",
        "-preset", PRESET,
        "-tune", "stillimage",
        "-b:v", VIDEO_BITRATE,
        "-maxrate", VIDEO_BITRATE,
        "-bufsize", f"{int(VIDEO_BITRATE.replace('k', '')) * 2}k",
        "-pix_fmt", "yuv420p",
        "-r", str(FRAMERATE),
        "-g", str(FRAMERATE * 2),       # Keyframe interval
        "-s", f"{STREAM_WIDTH}x{STREAM_HEIGHT}",
        "-c:a", "aac",
        "-b:a", AUDIO_BITRATE,
        "-ar", "44100",
        "-shortest",                    # End when audio ends
        "-f", "flv",
        rtmp_url,
    ]


def stream_track(audio_path: str, title: str, artist: str, source: str) -> bool:
    """Stream a single track to YouTube. Returns True if successful."""
    # Generate overlay for this track
    overlay_path = generate_overlay(title=title, artist=artist, source=source)

    cmd = build_ffmpeg_command(audio_path, overlay_path)
    print(f"[stream] Streaming: {title} by {artist} ({source})")

    try:
        process = subprocess.run(cmd, capture_output=True, timeout=900)  # 15 min max per track
        if process.returncode == 0:
            print(f"[stream] Finished: {title}")
            return True
        else:
            stderr_tail = process.stderr[-500:] if process.stderr else b""
            print(f"[stream] FFmpeg error (code {process.returncode}): {stderr_tail.decode('utf-8', errors='replace')}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[stream] Track timed out: {title}")
        return False
    except Exception as exc:
        print(f"[stream] Error streaming {title}: {exc}")
        return False


def main():
    """Main radio loop."""
    print("=" * 60)
    print("  🎛️  TizWildin 24/7 Radio Stream")
    print("=" * 60)

    # Validate RTMP key
    if not YOUTUBE_RTMP_KEY:
        print("[FATAL] YOUTUBE_RTMP_KEY not set. Cannot stream.")
        print("  Set it in .env or as an environment variable.")
        print("  Get your key from: https://studio.youtube.com → Go Live → Stream Key")
        sys.exit(1)

    # Generate default background if needed
    generate_default_background()

    # Bootstrap from SoundCloud if no local files
    local_files = scan_local_files(MUSIC_DIR)
    if not local_files:
        print("[init] No local music files found. Bootstrapping from SoundCloud...")
        downloaded = bootstrap_from_soundcloud()
        if downloaded == 0:
            print("[init] No tracks available. Place .mp3 files in the music/ directory.")
            print("[init] Waiting for tracks...")
            while not scan_local_files(MUSIC_DIR):
                time.sleep(30)

    # Initialize queue
    queue = RadioQueue()
    consecutive_failures = 0
    max_failures = 10

    print(f"[init] Radio ready. Streaming to {YOUTUBE_RTMP_URL}")
    print(f"[init] Resolution: {STREAM_WIDTH}x{STREAM_HEIGHT} @ {FRAMERATE}fps")
    print(f"[init] Video: {VIDEO_BITRATE} / Audio: {AUDIO_BITRATE} / Preset: {PRESET}")
    print()

    # ── Infinite stream loop ──
    while True:
        track_path = queue.next_track()

        if not track_path:
            print("[stream] No tracks available. Waiting 30s...")
            time.sleep(30)
            continue

        if not os.path.exists(track_path):
            print(f"[stream] File missing: {track_path}")
            continue

        # Extract title from filename
        stem = Path(track_path).stem
        # Clean up SC download names: "sc_12345_Artist Name - Track Title"
        if stem.startswith("sc_"):
            parts = stem.split("_", 2)
            title = parts[2] if len(parts) > 2 else stem
        else:
            title = stem

        artist = "TizWildin"
        source = queue.current_track.get("source", "playlist") if queue.current_track else "playlist"

        success = stream_track(track_path, title, artist, source)

        if success:
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            if consecutive_failures >= max_failures:
                print(f"[stream] {max_failures} consecutive failures. Waiting 60s before retry...")
                time.sleep(60)
                consecutive_failures = 0
            else:
                time.sleep(5)  # Brief pause before next track

        # Small gap between tracks
        time.sleep(2)


if __name__ == "__main__":
    main()
