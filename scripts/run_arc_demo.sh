#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/arc_service"
python3 -m pip install -r requirements.txt >/dev/null
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
