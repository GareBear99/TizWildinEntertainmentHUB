from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
import json
import zipfile

from app.services.account_service import get_account_summary
from app.services.activity_service import get_activity
from app.services.backup_service import export_backup
from app.services.diagnostics_service import export_account_diagnostics
from app.services.launchpad_service import get_launchpad
from app.services.readiness_service import get_readiness
from app.services.settings_service import get_settings
from app.services.store import ROOT

ARTIFACTS_DIR = ROOT.parents[1] / "artifacts"
SUPPORT_DIR = ARTIFACTS_DIR / "support_bundles"


def create_support_bundle(account_id: str, machine_id: str = "mac_demo", channel: str = "stable") -> dict:
    summary = get_account_summary(account_id)
    if not summary:
        return {"approved": False, "reason": "unknown_account"}

    diagnostics = export_account_diagnostics(account_id)
    backup = export_backup(tag=f"support_{account_id}")
    settings = get_settings(account_id)
    readiness = get_readiness(account_id, machine_id, channel)
    launchpad = get_launchpad(account_id, machine_id, channel)
    activity = get_activity(account_id, limit=50)

    SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    bundle_path = SUPPORT_DIR / f"{account_id}_{timestamp}_support_bundle.zip"

    payload = {
        "generatedAt": datetime.now(UTC).isoformat(),
        "accountId": account_id,
        "machineId": machine_id,
        "channel": channel,
        "summary": summary,
        "settings": settings,
        "readiness": readiness,
        "launchpad": launchpad,
        "activity": activity,
    }

    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("support_snapshot.json", json.dumps(payload, indent=2))
        diag_path = diagnostics.get("path")
        if diag_path and Path(diag_path).exists():
            zf.write(diag_path, arcname=Path(diag_path).name)
        backup_path = backup.get("path")
        if backup_path and Path(backup_path).exists():
            zf.write(backup_path, arcname=Path(backup_path).name)

    return {
        "approved": True,
        "accountId": account_id,
        "machineId": machine_id,
        "channel": channel,
        "path": str(bundle_path),
        "included": {
            "diagnostics": diagnostics.get("path"),
            "backup": backup.get("path"),
            "snapshot": "support_snapshot.json",
        },
    }
