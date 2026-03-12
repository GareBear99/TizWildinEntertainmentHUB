from pathlib import Path
import json
from app.services.catalog_service import load_catalog

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "entitlements.mock.json"

def load_entitlements():
    return json.loads(DATA_PATH.read_text())

def resolve_product_access(entitlement: dict, product_id: str) -> dict:
    catalog = load_catalog()
    product = next((p for p in catalog["products"] if p["productId"] == product_id), None)
    if not product:
        return {"allowed": False, "reason": "unknown_product", "features": []}

    license_class = product["licenseClass"]
    if license_class in {"FREE_OPEN", "FREE_LITE"}:
        return {"allowed": True, "reason": "free_access", "features": ["standard"]}

    if entitlement.get("billingState") == "payment_issue":
        return {"allowed": False, "reason": "payment_issue", "features": []}

    if entitlement.get("ownsEveryVST") and product.get("includedInOwnsEveryVST"):
        return {"allowed": True, "reason": "complete_collection", "features": ["pro", "full"]}

    if product_id in entitlement.get("ownedProducts", []):
        return {"allowed": True, "reason": "owned_product", "features": ["pro", "full"]}

    if product_id == "mixmaid" and "complete_collection" in entitlement.get("ownedBundles", []):
        return {"allowed": True, "reason": "bundle_rule", "features": ["pro", "full"]}

    return {"allowed": False, "reason": "not_owned", "features": []}
