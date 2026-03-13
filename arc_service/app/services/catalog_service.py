from app.services.store import load_catalog


def find_product(product_id: str) -> dict | None:
    catalog = load_catalog()
    return next((p for p in catalog.get("products", []) if p.get("productId") == product_id), None)
