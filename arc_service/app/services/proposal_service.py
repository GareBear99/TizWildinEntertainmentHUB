from app.models.domain import ProposalRequest
from app.services.catalog_service import load_catalog
from app.services.entitlement_service import load_entitlements, resolve_product_access


def decide_proposal(request: ProposalRequest) -> dict:
    ent = load_entitlements().get(request.accountId)
    catalog = load_catalog()
    if not ent:
        return {"proposalId": request.proposalId, "approved": False, "reason": "unknown_account"}

    if request.type == "install_missing":
        actions = []
        for product_id in request.requestedProducts:
            product = next((p for p in catalog["products"] if p["productId"] == product_id), None)
            if not product:
                actions.append({"productId": product_id, "action": "skip_unknown"})
                continue
            access = resolve_product_access(ent, product_id)
            if not access["allowed"] and product["licenseClass"] not in {"FREE_OPEN", "FREE_LITE"}:
                actions.append({"productId": product_id, "action": "purchase_required"})
                continue
            if product["status"] == "coming_soon":
                actions.append({"productId": product_id, "action": "coming_soon"})
            else:
                actions.append({"productId": product_id, "action": "download_or_build"})
        return {"proposalId": request.proposalId, "approved": True, "actions": actions}

    if request.type == "refresh_catalog":
        return {"proposalId": request.proposalId, "approved": True, "actions": ["reload_catalog", "rescan_local_state"]}

    return {"proposalId": request.proposalId, "approved": False, "reason": "unsupported_proposal_type"}
