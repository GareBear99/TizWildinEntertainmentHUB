from __future__ import annotations
from app.models.domain import InstallPlanRequest
from app.services.store import load_catalog, load_install_scans
from app.services.entitlement_service import get_entitlement, resolve_product_access
from app.services.release_service import get_release_manifest


def _latest_scan_by_machine(account_id: str, machine_id: str) -> dict:
    scans = load_install_scans()
    for entry in reversed(scans):
        if entry.get("accountId") == account_id and entry.get("machineId") == machine_id:
            return entry
    return {"products": []}


def _parse_version(value: str | None) -> tuple[int, ...]:
    if not value:
        return tuple()
    cleaned = value.strip().lower().lstrip("v")
    parts = []
    for raw in cleaned.split('.'):
        digits = ''.join(ch for ch in raw if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def _is_newer(candidate: str | None, installed: str | None) -> bool:
    if not candidate:
        return False
    if not installed:
        return True
    return _parse_version(candidate) > _parse_version(installed)


def build_install_plan(request: InstallPlanRequest) -> dict:
    entitlement = get_entitlement(request.accountId)
    if not entitlement:
        return {"approved": False, "reason": "unknown_account", "actions": []}

    catalog = load_catalog()
    manifests = get_release_manifest(channel=request.channel)
    latest_scan = _latest_scan_by_machine(request.accountId, request.machineId)
    installed = {p.get("productId"): p for p in latest_scan.get("products", [])}

    product_ids = request.requestedProducts or [p.get("productId") for p in catalog.get("products", [])]
    actions = []
    for product_id in product_ids:
        product = next((p for p in catalog.get("products", []) if p.get("productId") == product_id), None)
        if not product:
            actions.append({"productId": product_id, "action": "skip_unknown"})
            continue

        access = resolve_product_access(entitlement, product_id)
        if product.get("status") == "coming_soon":
            actions.append({"productId": product_id, "action": "coming_soon"})
            continue
        if not access["allowed"] and product.get("licenseClass") not in {"FREE_OPEN", "FREE_LITE"}:
            actions.append({"productId": product_id, "action": "purchase_required"})
            continue

        manifest = manifests.get(product_id, {})
        if not manifest:
            actions.append({"productId": product_id, "action": "release_unavailable", "channel": request.channel})
            continue

        installed_entry = installed.get(product_id)
        latest_version = manifest.get("latestVersion")
        installed_version = None if not installed_entry else installed_entry.get("localVersion") or installed_entry.get("runtimeVersion")

        if not installed_entry or installed_entry.get("installState") in {"missing", "not_installed"}:
            action = "install_free_source" if product.get("licenseClass") in {"FREE_OPEN", "FREE_LITE"} else "build_from_source"
            actions.append({"productId": product_id, "action": action, "targetVersion": latest_version, "channel": request.channel})
            continue

        if _is_newer(latest_version, installed_version):
            actions.append({"productId": product_id, "action": "update_available", "installedVersion": installed_version, "targetVersion": latest_version, "channel": request.channel})
            continue

        actions.append({"productId": product_id, "action": "already_current", "targetVersion": latest_version, "channel": request.channel})

    return {"approved": True, "machineId": request.machineId, "channel": request.channel, "actions": actions}
