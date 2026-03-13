from __future__ import annotations
from datetime import datetime, UTC
from pathlib import Path

from app.services.store import (
    ROOT,
    load_auth_tokens,
    load_entitlements,
    load_install_receipts,
    load_install_scans,
    load_release_manifests,
    load_seats,
    load_webhooks,
    save_auth_tokens,
    save_entitlements,
    save_install_receipts,
    save_install_scans,
    save_release_manifests,
    save_seats,
    save_webhooks,
)
import json

BACKUP_DIR = ROOT.parent.parent / 'artifacts' / 'backups'


def _snapshot_payload() -> dict:
    return {
        'createdAt': datetime.now(UTC).isoformat(),
        'service': 'TizWildin Hub ARC',
        'version': '1.0.0',
        'data': {
            'entitlements': load_entitlements(),
            'seats': load_seats(),
            'installScans': load_install_scans(),
            'installReceipts': load_install_receipts(),
            'webhooks': load_webhooks(),
            'releaseManifests': load_release_manifests(),
            'authTokens': load_auth_tokens(),
        },
    }


def export_backup(tag: str | None = None) -> dict:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
    safe_tag = (tag or 'snapshot').replace(' ', '_').replace('/', '_')[:40]
    path = BACKUP_DIR / f'{stamp}_{safe_tag}.json'
    payload = _snapshot_payload()
    path.write_text(json.dumps(payload, indent=2))
    return {'approved': True, 'path': str(path), 'snapshot': payload}


def list_backups() -> dict:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for path in sorted(BACKUP_DIR.glob('*.json'), reverse=True):
        items.append({'name': path.name, 'path': str(path), 'sizeBytes': path.stat().st_size})
    return {'approved': True, 'backups': items}


def restore_backup(path: str) -> dict:
    backup_path = Path(path)
    if not backup_path.exists():
        return {'approved': False, 'reason': 'backup_not_found'}
    payload = json.loads(backup_path.read_text())
    data = payload.get('data', {})
    save_entitlements(data.get('entitlements', {}))
    save_seats(data.get('seats', {}))
    save_install_scans(data.get('installScans', []))
    save_install_receipts(data.get('installReceipts', []))
    save_webhooks(data.get('webhooks', []))
    save_release_manifests(data.get('releaseManifests', {}))
    save_auth_tokens(data.get('authTokens', {}))
    return {'approved': True, 'restoredFrom': str(backup_path), 'createdAt': payload.get('createdAt', '')}
