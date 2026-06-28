"""Radio service configuration — all values from environment variables."""
from __future__ import annotations
import os

# YouTube RTMP
YOUTUBE_RTMP_URL = os.environ.get("YOUTUBE_RTMP_URL", "rtmp://a.rtmp.youtube.com/live2")
YOUTUBE_RTMP_KEY = os.environ.get("YOUTUBE_RTMP_KEY", "")

# SoundCloud default playlist (URL to a public SC playlist)
SOUNDCLOUD_PLAYLIST_URL = os.environ.get("SOUNDCLOUD_PLAYLIST_URL", "https://soundcloud.com/tizwildin/sets")
SOUNDCLOUD_CLIENT_ID = os.environ.get("SOUNDCLOUD_CLIENT_ID", "")

# Directories
MUSIC_DIR = os.environ.get("MUSIC_DIR", "/app/music")
SUBMISSIONS_DIR = os.environ.get("SUBMISSIONS_DIR", "/app/submissions")
ASSETS_DIR = os.environ.get("ASSETS_DIR", "/app/assets")

# Stream settings
STREAM_WIDTH = int(os.environ.get("STREAM_WIDTH", "1280"))
STREAM_HEIGHT = int(os.environ.get("STREAM_HEIGHT", "720"))
VIDEO_BITRATE = os.environ.get("VIDEO_BITRATE", "750k")
AUDIO_BITRATE = os.environ.get("AUDIO_BITRATE", "128k")
FRAMERATE = int(os.environ.get("FRAMERATE", "30"))
PRESET = os.environ.get("PRESET", "veryfast")

# Overlay
BACKGROUND_IMAGE = os.environ.get("BACKGROUND_IMAGE", os.path.join(ASSETS_DIR, "background.png"))
LOGO_PATH = os.environ.get("LOGO_PATH", os.path.join(ASSETS_DIR, "logo.png"))
OVERLAY_OUTPUT = os.environ.get("OVERLAY_OUTPUT", "/tmp/now_playing.png")

# Queue
HISTORY_FILE = os.environ.get("HISTORY_FILE", "/app/data/history.json")
QUEUE_FILE = os.environ.get("QUEUE_FILE", "/app/data/queue.json")
