from __future__ import annotations
import uuid
from datetime import datetime, UTC
from app.models.domain import SeatAssignment
from app.services.store import load_entitlements, load_seats, save_seats


def list_seats(account_id: str):
    seats = load_seats()
    return [SeatAssignment(**s) for s in seats.get(account_id, [])]


def assign_seat(account_id: str, machine_id: str, product_id: str) -> dict:
    entitlements = load_entitlements()
    seats = load_seats()

    entitlement = entitlements.get(account_id)
    if not entitlement:
        return {"approved": False, "reason": "unknown_account"}

    max_seats = 1 + int(entitlement.get("extraSeatQuantity", 0))
    account_seats = seats.setdefault(account_id, [])

    existing = next((s for s in account_seats if s["machineId"] == machine_id and s.get("status", "active") == "active"), None)
    if existing:
        existing["productId"] = product_id
        existing["lastSeenAt"] = datetime.now(UTC).isoformat()
        if not existing.get("assignedAt"):
            existing["assignedAt"] = existing["lastSeenAt"]
        save_seats(seats)
        return {"approved": True, "reason": "existing_machine", "seat": existing}

    active_count = sum(1 for s in account_seats if s.get("status", "active") == "active")
    if active_count >= max_seats:
        return {"approved": False, "reason": "seat_limit_reached", "maxSeats": max_seats}

    now = datetime.now(UTC).isoformat()
    seat = {"seatId": f"seat_{uuid.uuid4().hex[:10]}", "accountId": account_id, "machineId": machine_id, "productId": product_id, "status": "active", "assignedAt": now, "lastSeenAt": now}
    account_seats.append(seat)
    save_seats(seats)
    return {"approved": True, "reason": "seat_assigned", "seat": seat}


def release_seat(account_id: str, seat_id: str) -> dict:
    seats = load_seats()
    target = next((s for s in seats.get(account_id, []) if s.get("seatId") == seat_id), None)
    if not target:
        return {"approved": False, "reason": "seat_not_found"}
    target["status"] = "released"
    save_seats(seats)
    return {"approved": True, "reason": "seat_released", "seat": target}
