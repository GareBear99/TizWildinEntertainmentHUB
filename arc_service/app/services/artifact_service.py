from __future__ import annotations
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ARTIFACTS_DIR = Path(__file__).resolve().parents[3] / "artifacts"
STAGED_DIR = ARTIFACTS_DIR / "staged"


def sha256_for_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_demo_artifact(product_id: str, version: str) -> dict:
    STAGED_DIR.mkdir(parents=True, exist_ok=True)
    payload_dir = STAGED_DIR / f"{product_id}-{version}"
    payload_dir.mkdir(parents=True, exist_ok=True)
    (payload_dir / 'README.txt').write_text(f"{product_id} {version} staged artifact for Tiz HUB\n")
    (payload_dir / 'manifest.json').write_text(json.dumps({
        'productId': product_id,
        'version': version,
        'builtBy': 'ARC demo artifact service',
    }, indent=2))
    zip_path = STAGED_DIR / f"{product_id}-{version}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for child in payload_dir.rglob('*'):
            zf.write(child, arcname=f"{product_id}-{version}/{child.relative_to(payload_dir)}")
    return {'artifactPath': str(zip_path), 'sha256': sha256_for_file(zip_path), 'signature': 'arc-demo-signed-local'}


def verify_artifact(path_str: str, expected_sha256: str | None = None, expected_signature: str | None = None) -> dict:
    if not path_str:
        return {'ok': False, 'reason': 'artifact_missing'}
    path = Path(path_str)
    if not path.exists() or path.is_dir():
        return {'ok': False, 'reason': 'artifact_missing'}
    actual_sha = sha256_for_file(path)
    if expected_sha256 and actual_sha != expected_sha256:
        return {'ok': False, 'reason': 'sha256_mismatch', 'actualSha256': actual_sha}
    if expected_signature and expected_signature not in {'arc-demo-signed', 'arc-demo-signed-local'}:
        return {'ok': False, 'reason': 'signature_rejected', 'actualSha256': actual_sha}
    return {'ok': True, 'actualSha256': actual_sha}


def install_artifact(path_str: str, install_root: str | Path, product_id: str, version: str) -> dict:
    path = Path(path_str)
    root = Path(install_root)
    target_dir = root / product_id / version
    target_dir.mkdir(parents=True, exist_ok=True)

    if path.suffix.lower() == '.zip':
        with zipfile.ZipFile(path, 'r') as zf:
            zf.extractall(target_dir)
        artifact_mode = 'zip'
    elif path.is_dir():
        dest = target_dir / path.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(path, dest)
        artifact_mode = 'directory'
    else:
        shutil.copy2(path, target_dir / path.name)
        artifact_mode = 'file'

    current = root / product_id / 'CURRENT'
    current.write_text(version)
    return {'installedPath': str(target_dir), 'artifactModeResolved': artifact_mode}
