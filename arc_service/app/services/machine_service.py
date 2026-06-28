from app.services.store import load_install_scans, load_install_receipts
from app.services.seat_service import list_seats


def list_machines(account_id: str) -> list[dict]:
    machine_map: dict[str, dict] = {}
    for seat in list_seats(account_id):
        entry = machine_map.setdefault(seat.machineId, {"machineId": seat.machineId, "seatProducts": set(), "installedProducts": [], "lastScanAt": None, "receiptCount": 0, "productCount": 0})
        entry["seatProducts"].add(seat.productId)

    for scan in load_install_scans():
        if scan.get("accountId") != account_id:
            continue
        entry = machine_map.setdefault(scan.get("machineId"), {"machineId": scan.get("machineId"), "seatProducts": set(), "installedProducts": [], "lastScanAt": None, "receiptCount": 0, "productCount": 0})
        entry["lastScanAt"] = scan.get("timestamp")
        entry["installedProducts"] = [
            {
                "productId": p.get("productId"),
                "version": p.get("localVersion"),
                "state": p.get("installState"),
                "channel": p.get("channel", "stable"),
            }
            for p in scan.get("products", [])
        ]
        entry["productCount"] = len(entry["installedProducts"])

    for receipt in load_install_receipts():
        if receipt.get("accountId") != account_id:
            continue
        entry = machine_map.setdefault(receipt.get("machineId"), {"machineId": receipt.get("machineId"), "seatProducts": set(), "installedProducts": [], "lastScanAt": None, "receiptCount": 0, "productCount": 0})
        entry["receiptCount"] += 1

    result = []
    for machine in machine_map.values():
        machine["seatProducts"] = sorted(machine["seatProducts"])
        result.append(machine)
    return sorted(result, key=lambda m: m["machineId"])
