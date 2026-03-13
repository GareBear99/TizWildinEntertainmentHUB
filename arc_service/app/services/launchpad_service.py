from __future__ import annotations

from app.models.domain import DownloadPlanRequest, InstallPlanRequest
from app.services.account_service import get_account_summary
from app.services.download_service import build_download_plan
from app.services.install_plan_service import build_install_plan
from app.services.release_service import get_release_manifest
from app.services.settings_service import get_settings
from app.services.store import load_catalog


def get_launchpad(account_id: str, machine_id: str, channel: str = 'stable') -> dict | None:
    summary = get_account_summary(account_id)
    if not summary:
        return None

    catalog = load_catalog().get('products', [])
    releases = get_release_manifest(channel=channel)
    install_plan = build_install_plan(InstallPlanRequest(
        accountId=account_id,
        machineId=machine_id,
        requestedProducts=[],
        channel=channel,
    ))
    download_plan = build_download_plan(DownloadPlanRequest(
        accountId=account_id,
        machineId=machine_id,
        requestedProducts=[],
        channel=channel,
    ))

    actions = install_plan.get('actions', [])
    action_counts: dict[str, int] = {}
    for action in actions:
        key = action.get('action', 'unknown')
        action_counts[key] = action_counts.get(key, 0) + 1

    settings = get_settings(account_id)

    return {
        'approved': True,
        'accountId': account_id,
        'machineId': machine_id,
        'channel': channel,
        'overview': {
            'catalogCount': len(catalog),
            'releaseCount': len(releases),
            'downloadableCount': len(download_plan.get('downloads', [])),
            'pendingUpdateCount': action_counts.get('update_available', 0),
            'installableCount': action_counts.get('install_free_source', 0) + action_counts.get('build_from_source', 0),
            'alreadyCurrentCount': action_counts.get('already_current', 0),
            'lockedCount': action_counts.get('purchase_required', 0),
            'seatUsage': {
                'active': summary.get('stats', {}).get('activeSeatCount', 0),
                'max': summary.get('stats', {}).get('maxSeats', 0),
            },
        },
        'accountSummary': summary,
        'installPlan': install_plan,
        'downloadPlan': download_plan,
        'releaseChannels': sorted({m.get('channel', 'stable') for m in get_release_manifest().values()}),
        'settings': settings,
    }
