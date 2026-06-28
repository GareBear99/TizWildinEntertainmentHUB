from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen

from app.services.artifact_service import ARTIFACTS_DIR, sha256_for_file

DOWNLOADS_DIR = ARTIFACTS_DIR / "downloads"


def fetch_artifact(artifact_url: str, product_id: str, version: str, expected_sha256: str | None = None) -> dict:
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(artifact_url.split("?")[0]).suffix or ".bin"
    target = DOWNLOADS_DIR / f"{product_id}-{version}{suffix}"
    with urlopen(artifact_url) as resp, target.open("wb") as fh:
        fh.write(resp.read())
    actual_sha = sha256_for_file(target)
    ok = not expected_sha256 or actual_sha == expected_sha256
    return {
        "ok": ok,
        "artifactPath": str(target),
        "actualSha256": actual_sha,
        "reason": "downloaded" if ok else "sha256_mismatch",
    }
