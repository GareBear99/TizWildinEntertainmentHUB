"""Queue manager — resolves SoundCloud playlists, manages local files + submission queue."""
from __future__ import annotations

import json
import os
import random
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

from config import HISTORY_FILE, MUSIC_DIR, QUEUE_FILE, SOUNDCLOUD_CLIENT_ID, SOUNDCLOUD_PLAYLIST_URL, SUBMISSIONS_DIR

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".opus"}


def _ensure_dir(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _load_json(path: str) -> list:
    if os.path.exists(path):
        try:
            return json.loads(Path(path).read_text())
        except Exception:
            return []
    return []


def _save_json(path: str, data: list) -> None:
    _ensure_dir(path)
    Path(path).write_text(json.dumps(data, indent=2))


# ── SoundCloud playlist resolution ──────────────────────────────────
def resolve_soundcloud_playlist() -> list[dict]:
    """Resolve a SoundCloud playlist URL to a list of streamable track URLs.
    
    Uses yt-dlp which handles SoundCloud playlists natively and extracts
    direct audio URLs without needing the SC API.
    """
    if not SOUNDCLOUD_PLAYLIST_URL:
        return []
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--dump-json", SOUNDCLOUD_PLAYLIST_URL],
            capture_output=True, text=True, timeout=120,
        )
        tracks = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            try:
                info = json.loads(line)
                tracks.append({
                    "id": info.get("id", ""),
                    "title": info.get("title", "Unknown"),
                    "artist": info.get("uploader", "TizWildin"),
                    "url": info.get("url") or info.get("webpage_url", ""),
                    "source": "soundcloud",
                })
            except json.JSONDecodeError:
                continue
        return tracks
    except Exception as exc:
        print(f"[queue] SoundCloud resolve failed: {exc}")
        return []


def download_sc_track(track: dict, output_dir: str = MUSIC_DIR) -> str | None:
    """Download a SoundCloud track to local file using yt-dlp. Returns file path."""
    os.makedirs(output_dir, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in track["title"])[:80]
    output_path = os.path.join(output_dir, f"sc_{track['id']}_{safe_name}.mp3")
    if os.path.exists(output_path):
        return output_path
    try:
        subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", "-o", output_path, track["url"]],
            capture_output=True, timeout=180,
        )
        if os.path.exists(output_path):
            return output_path
    except Exception as exc:
        print(f"[queue] Download failed for {track['title']}: {exc}")
    return None


# ── Local file scanner ──────────────────────────────────────────────
def scan_local_files(directory: str = MUSIC_DIR) -> list[str]:
    """Scan a directory for audio files."""
    if not os.path.isdir(directory):
        return []
    return sorted(
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if Path(f).suffix.lower() in AUDIO_EXTS and os.path.isfile(os.path.join(directory, f))
    )


def scan_submissions(directory: str = SUBMISSIONS_DIR) -> list[str]:
    """Scan submissions directory for promotional uploads."""
    return scan_local_files(directory)


# ── Queue management ────────────────────────────────────────────────
class RadioQueue:
    """Manages the play queue with submission priority."""

    def __init__(self):
        self.playlist: list[str] = []
        self.submission_queue: list[str] = []
        self.history: list[dict] = _load_json(HISTORY_FILE)
        self.current_track: dict | None = None
        self._playlist_index = 0

    def refresh_playlist(self) -> None:
        """Refresh playlist from local files (downloaded from SC or manually placed)."""
        files = scan_local_files(MUSIC_DIR)
        if files != self.playlist:
            self.playlist = files
            random.shuffle(self.playlist)
            self._playlist_index = 0
            print(f"[queue] Playlist refreshed: {len(self.playlist)} tracks")

    def refresh_submissions(self) -> None:
        """Check for new promotional submissions."""
        subs = scan_submissions(SUBMISSIONS_DIR)
        new_subs = [s for s in subs if s not in self.submission_queue]
        if new_subs:
            self.submission_queue.extend(new_subs)
            print(f"[queue] {len(new_subs)} new submissions queued")

    def next_track(self) -> str | None:
        """Get next track — submissions take priority, then shuffled playlist."""
        # Check for submissions first (promotional priority)
        self.refresh_submissions()
        if self.submission_queue:
            track_path = self.submission_queue.pop(0)
            self._log_play(track_path, source="submission")
            return track_path

        # Fall back to playlist
        self.refresh_playlist()
        if not self.playlist:
            return None

        if self._playlist_index >= len(self.playlist):
            random.shuffle(self.playlist)
            self._playlist_index = 0

        track_path = self.playlist[self._playlist_index]
        self._playlist_index += 1
        self._log_play(track_path, source="playlist")
        return track_path

    def _log_play(self, path: str, source: str = "playlist") -> None:
        """Log track to history."""
        name = Path(path).stem
        entry = {
            "file": Path(path).name,
            "title": name,
            "source": source,
            "played_at": datetime.now(UTC).isoformat(),
        }
        self.current_track = entry
        self.history.insert(0, entry)
        self.history = self.history[:200]  # Keep last 200
        _save_json(HISTORY_FILE, self.history)
        print(f"[queue] Now playing: {name} ({source})")

    def get_status(self) -> dict:
        """Return current queue status for API."""
        return {
            "nowPlaying": self.current_track,
            "queueLength": len(self.submission_queue),
            "playlistLength": len(self.playlist),
            "submissionsPending": len(self.submission_queue),
        }

    def get_history(self, limit: int = 50) -> list[dict]:
        return self.history[:limit]


# ── SoundCloud playlist bootstrap ───────────────────────────────────
def bootstrap_from_soundcloud() -> int:
    """Download tracks from the configured SoundCloud playlist to MUSIC_DIR."""
    print(f"[bootstrap] Resolving SoundCloud playlist: {SOUNDCLOUD_PLAYLIST_URL}")
    tracks = resolve_soundcloud_playlist()
    if not tracks:
        print("[bootstrap] No tracks resolved from SoundCloud")
        return 0

    downloaded = 0
    for track in tracks:
        path = download_sc_track(track)
        if path:
            downloaded += 1
            print(f"[bootstrap] Downloaded: {track['title']}")

    print(f"[bootstrap] Downloaded {downloaded}/{len(tracks)} tracks")
    return downloaded
