from __future__ import annotations

from app.models.domain import PreflightRequest
from app.services.account_service import get_account_summary
from app.services.download_service import build_download_plan
from app.services.install_plan_service import build_install_plan
from app.services.launchpad_service import get_launchpad
from app.services.preflight_service import run_preflight
from app.services.readiness_service import get_readiness
from app.services.settings_service import get_settings


def build_sync_status(request: PreflightRequest) -> dict:
    settings = get_settings(request.accountId)
    channel = request.channel or settings.get("preferredChannel", "stable")
    requested_products = request.requestedProducts or []

    readiness = get_readiness(request.accountId, request.machineId, channel)
    launchpad = get_launchpad(request.accountId, request.machineId, channel)
    install_plan = build_install_plan(request.model_copy(update={"channel": channel}))
    download_plan = build_download_plan(request.model_copy(update={"channel": channel}))
    preflight = run_preflight(request.accountId, request.machineId, requested_products, channel)
    summary = get_account_summary(request.accountId)

    approved = bool(readiness and readiness.get("approved") and launchpad and install_plan.get("approved") and download_plan.get("approved") and preflight.get("approved"))
    actions = install_plan.get("actions", [])
    blockers = list(preflight.get("warnings", []))
    if not readiness.get("ready", False):
        blockers.extend(readiness.get("blockers", []))

    return {
        "approved": approved,
        "accountId": request.accountId,
        "machineId": request.machineId,
        "channel": channel,
        "settings": settings,
        "summary": summary,
        "readiness": readiness,
        "launchpad": launchpad,
        "preflight": preflight,
        "installPlan": install_plan,
        "downloadPlan": download_plan,
        "nextAction": "execute" if approved and len(actions) > 0 else ("idle" if approved else "fix_blockers"),
        "counts": {
            "installActions": len(actions),
            "downloads": len(download_plan.get("downloads", [])),
            "warnings": len(preflight.get("warnings", [])),
            "blockers": len(blockers),
        },
        "blockers": blockers,
    }
