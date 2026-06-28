from __future__ import annotations

from app.services.launchpad_service import get_launchpad
from app.services.settings_service import get_settings


def get_readiness(account_id: str, machine_id: str | None = None, channel: str | None = None) -> dict | None:
    settings = get_settings(account_id)
    target_machine = machine_id or settings.get("machineId", "mac_demo")
    target_channel = channel or settings.get("preferredChannel", "stable")
    launchpad = get_launchpad(account_id, target_machine, target_channel)
    if not launchpad:
        return None
    overview = launchpad.get("overview", {})
    blockers = []
    if overview.get("downloadableCount", 0) == 0:
        blockers.append("no_downloadable_products")
    if overview.get("seatUsage", {}).get("max", 0) <= 0:
        blockers.append("no_seat_capacity")
    ready = len(blockers) == 0
    return {
        "approved": True,
        "accountId": account_id,
        "machineId": target_machine,
        "channel": target_channel,
        "ready": ready,
        "score": 100 if ready else 70,
        "blockers": blockers,
        "overview": overview,
        "settings": settings,
    }
