from __future__ import annotations

from app.services.account_service import get_account_summary
from app.services.activity_service import get_activity
from app.services.readiness_service import get_readiness
from app.services.release_service import get_release_manifest
from app.services.settings_service import get_settings


def audit_account(account_id: str, machine_id: str = "mac_demo", channel: str = "stable") -> dict:
    summary = get_account_summary(account_id)
    if not summary:
        return {"approved": False, "reason": "unknown_account"}

    readiness = get_readiness(account_id, machine_id, channel)
    settings = get_settings(account_id)
    activity = get_activity(account_id, limit=20)
    releases = get_release_manifest(channel=channel)

    stats = summary.get("stats", {})
    blockers = list(readiness.get("blockers", [])) if readiness else []
    warnings = []

    if settings.get("arcBaseUrl", "").startswith("http://127.0.0.1"):
        warnings.append("arc_base_url_is_localhost")
    if not releases:
        blockers.append("no_release_manifests_for_channel")
    if stats.get("activeSeatCount", 0) >= stats.get("maxSeats", 0):
        warnings.append("seat_capacity_reached")

    score = 100
    score -= 20 * len(blockers)
    score -= 5 * len(warnings)
    score = max(0, score)

    return {
        "approved": True,
        "accountId": account_id,
        "machineId": machine_id,
        "channel": channel,
        "score": score,
        "grade": "A" if score >= 90 else ("B" if score >= 75 else ("C" if score >= 60 else "D")),
        "readiness": readiness,
        "warnings": warnings,
        "blockers": blockers,
        "counts": {
            "ownedProducts": len(summary.get("entitlements", {}).get("ownedProducts", [])),
            "activeSeats": stats.get("activeSeatCount", 0),
            "maxSeats": stats.get("maxSeats", 0),
            "machines": len(summary.get("machines", [])),
            "receipts": len(summary.get("receipts", [])),
            "activityItems": activity.get("count", 0),
            "releaseManifests": len(releases),
        },
    }
