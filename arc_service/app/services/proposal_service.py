from app.models.domain import ProposalRequest
from app.services.store import load_catalog
from app.services.entitlement_service import get_entitlement, resolve_product_access


def decide_proposal(request: ProposalRequest) -> dict:
    entitlement = get_entitlement(request.accountId)
    catalog = load_catalog()
    if not entitlement:
        return {"proposalId": request.proposalId, "approved": False, "reason": "unknown_account"}

    if request.type == "refresh_catalog":
        return {
            "proposalId": request.proposalId,
            "approved": True,
            "actions": ["reload_catalog", "rescan_local_state", "refresh_entitlements", "refresh_seats"],
        }

    if request.type == "check_updates":
        actions = [{"action": "compare_installed_vs_release_manifest", "scope": "all_products"}]
        return {"proposalId": request.proposalId, "approved": True, "actions": actions}

    if request.type == "install_missing":
        actions = []
        for product_id in request.requestedProducts:
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

            if product.get("status") == "source_ready":
                actions.append({"productId": product_id, "action": "build_from_source"})
            else:
                actions.append({"productId": product_id, "action": "download_binary"})

        return {"proposalId": request.proposalId, "approved": True, "actions": actions}

    return {"proposalId": request.proposalId, "approved": False, "reason": "unsupported_proposal_type"}
