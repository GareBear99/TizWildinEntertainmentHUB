from __future__ import annotations
from datetime import datetime, UTC
from pathlib import Path
import json
from app.services.account_service import get_account_summary
from app.services.release_service import get_release_manifest
from app.services.store import load_install_receipts, load_webhooks, load_seats, load_auth_tokens

DIAG_DIR = Path(__file__).resolve().parents[3] / "artifacts" / "diagnostics"

def export_account_diagnostics(account_id: str) -> dict:
    summary = get_account_summary(account_id)
    if not summary:
        return {"approved": False, "reason": "unknown_account"}

    receipts = [r for r in load_install_receipts() if r.get("accountId") == account_id]
    seats = load_seats().get(account_id, [])
    tokens = [dict(token=t, **record) for t, record in load_auth_tokens().items() if record.get("accountId") == account_id]
    webhooks = []
    for event in load_webhooks():
        payload = event.get("payload") or {}
        if payload.get("accountId") == account_id:
            webhooks.append(event)

    report = {
        "exportedAt": datetime.now(UTC).isoformat(),
        "accountId": account_id,
        "serviceVersion": "0.8.0",
        "summary": summary,
        "receipts": receipts[-100:],
        "seats": seats,
        "activeTokens": tokens,
        "webhooks": webhooks[-100:],
        "releases": get_release_manifest(),
    }
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    out = DIAG_DIR / f"{account_id}_diagnostics.json"
    out.write_text(json.dumps(report, indent=2))
    return {"approved": True, "accountId": account_id, "path": str(out), "report": report}
