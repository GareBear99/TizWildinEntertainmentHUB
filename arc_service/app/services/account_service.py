from app.services.store import load_catalog, load_entitlements, load_install_scans, load_install_receipts
from app.services.seat_service import list_seats
from app.services.machine_service import list_machines

def get_account_summary(account_id: str) -> dict | None:
    entitlement = load_entitlements().get(account_id)
    if not entitlement:
        return None

    catalog = load_catalog()
    seats = [s.model_dump() for s in list_seats(account_id)]
    scans = [s for s in load_install_scans() if s.get("accountId") == account_id]
    latest_scan = scans[-1] if scans else {"products": []}
    receipts = [r for r in load_install_receipts() if r.get("accountId") == account_id]

    total_products = len(catalog.get("products", []))
    free_products = sum(1 for p in catalog.get("products", []) if p.get("licenseClass", "").startswith("FREE"))
    owned_direct = len(entitlement.get("ownedProducts", []))

    return {
        "accountId": account_id,
        "entitlements": entitlement,
        "stats": {
            "totalCatalogProducts": total_products,
            "freeProducts": free_products,
            "ownedDirectProducts": owned_direct,
            "activeSeatCount": len([s for s in seats if s.get("status") == "active"]),
            "maxSeats": 1 + int(entitlement.get("extraSeatQuantity", 0)),
            "lastScanProductCount": len(latest_scan.get("products", [])),
            "installReceiptCount": len(receipts),
            "machineCount": len(list_machines(account_id)),
        },
        "latestInstallScan": latest_scan,
        "seats": seats,
        "machines": list_machines(account_id),
        "recentReceipts": receipts[-10:],
    }
