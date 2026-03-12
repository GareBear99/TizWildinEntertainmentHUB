from pathlib import Path
import json
import uuid
from app.models.domain import SeatAssignment

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "seats.mock.json"
ENT_PATH = Path(__file__).resolve().parent.parent / "data" / "entitlements.mock.json"

def _load_json(path: Path):
    return json.loads(path.read_text())

def _save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2))

def list_seats(account_id: str):
    seats = _load_json(DATA_PATH)
    return [SeatAssignment(**s) for s in seats.get(account_id, [])]

def assign_seat(account_id: str, machine_id: str, product_id: str) -> dict:
    entitlements = _load_json(ENT_PATH)
    seats = _load_json(DATA_PATH)

    account_ent = entitlements.get(account_id)
    if not account_ent:
        return {"approved": False, "reason": "unknown_account"}

    max_seats = 1 + int(account_ent.get("extraSeatQuantity", 0))
    account_seats = seats.setdefault(account_id, [])

    existing = next((s for s in account_seats if s["machineId"] == machine_id), None)
    if existing:
        existing["productId"] = product_id
        _save_json(DATA_PATH, seats)
        return {"approved": True, "reason": "existing_machine", "seat": existing}

    if len(account_seats) >= max_seats:
        return {"approved": False, "reason": "seat_limit_reached", "maxSeats": max_seats}

    seat = {
        "seatId": f"seat_{uuid.uuid4().hex[:10]}",
        "accountId": account_id,
        "machineId": machine_id,
        "productId": product_id,
        "status": "active"
    }
    account_seats.append(seat)
    _save_json(DATA_PATH, seats)
    return {"approved": True, "reason": "seat_assigned", "seat": seat}
