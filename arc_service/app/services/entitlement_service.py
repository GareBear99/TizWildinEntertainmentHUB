from app.db import get_db, fetch_account
from app.services.catalog_service import load_catalog


def load_entitlements() -> dict:
    """Return a dict keyed by account_id (matches old JSON shape for compat)."""
    with get_db() as conn:
        rows = conn.execute("SELECT account_id FROM accounts").fetchall()
        return {
            r["account_id"]: fetch_account(conn, r["account_id"])
            for r in rows
        }


def get_entitlement(account_id: str) -> dict | None:
    """Fetch a single account's entitlement from the DB."""
    with get_db() as conn:
        return fetch_account(conn, account_id)


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
