from __future__ import annotations

from app.services.account_service import get_account_summary
from app.services.download_service import build_download_plan
from app.services.install_plan_service import build_install_plan
from app.services.machine_service import list_machines
from app.models.domain import DownloadPlanRequest, InstallPlanRequest


def run_preflight(account_id: str, machine_id: str, requested_products: list[str], channel: str = 'stable') -> dict:
    summary = get_account_summary(account_id)
    if not summary:
        return {'approved': False, 'reason': 'account_not_found'}

    install_plan = build_install_plan(InstallPlanRequest(accountId=account_id, machineId=machine_id, requestedProducts=requested_products, channel=channel))
    download_plan = build_download_plan(DownloadPlanRequest(accountId=account_id, machineId=machine_id, requestedProducts=requested_products, channel=channel))
    machines = list_machines(account_id)

    warnings = []
    stats = summary.get('stats', {})
    if int(stats.get('activeSeatCount', 0)) >= int(stats.get('maxSeats', 0)):
        warnings.append('seat_capacity_full')
    if not download_plan.get('downloads'):
        warnings.append('no_downloads_available')
    for action in install_plan.get('actions', []):
        if action.get('action') in {'install_locked', 'not_owned'}:
            warnings.append(f"locked:{action.get('productId')}")
        if action.get('action') == 'update_available':
            warnings.append(f"update_available:{action.get('productId')}")
    for machine in machines:
        if machine.get('machineId') == machine_id and int(machine.get('productCount', 0)) == 0:
            warnings.append('machine_has_no_installs')
    warnings = sorted(set(warnings))
    return {
        'approved': True,
        'accountId': account_id,
        'machineId': machine_id,
        'channel': channel,
        'warnings': warnings,
        'summary': summary,
        'installPlan': install_plan,
        'downloadPlan': download_plan,
    }
