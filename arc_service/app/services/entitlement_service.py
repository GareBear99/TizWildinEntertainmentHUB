from app.services.store import load_entitlements
from app.services.catalog_service import find_product


def get_entitlement(account_id: str) -> dict | None:
    return load_entitlements().get(account_id)


def resolve_product_access(entitlement: dict, product_id: str) -> dict:
    product = find_product(product_id)
    if not product:
        return {"allowed": False, "reason": "unknown_product", "features": []}

    license_class = product.get("licenseClass")
    if license_class in {"FREE_OPEN", "FREE_LITE"}:
        features = ["standard"]
        if license_class == "FREE_LITE":
            features.append("lite")
        return {"allowed": True, "reason": "free_access", "features": features}

    if entitlement.get("billingState") == "payment_issue":
        return {"allowed": False, "reason": "payment_issue", "features": []}

    if entitlement.get("ownsEveryVST") and product.get("includedInOwnsEveryVST"):
        return {"allowed": True, "reason": "complete_collection", "features": ["pro", "full"]}

    if product_id in entitlement.get("ownedProducts", []):
        return {"allowed": True, "reason": "owned_product", "features": ["pro", "full"]}

    if product_id == "mixmaid" and "complete_collection" in entitlement.get("ownedBundles", []):
        return {"allowed": True, "reason": "bundle_rule", "features": ["pro", "full"]}

    return {"allowed": False, "reason": "not_owned", "features": []}
