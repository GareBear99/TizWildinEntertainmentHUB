import uuid
from app.db import get_db, fetch_account, fetch_seats
from app.models.domain import SeatAssignment


def list_seats(account_id: str) -> list[SeatAssignment]:
    with get_db() as conn:
        rows = fetch_seats(conn, account_id)
    return [SeatAssignment(**s) for s in rows]


def assign_seat(account_id: str, machine_id: str, product_id: str) -> dict:
    with get_db() as conn:
        account = fetch_account(conn, account_id)
        if not account:
            return {"approved": False, "reason": "unknown_account"}

        max_seats = 1 + int(account.get("extraSeatQuantity", 0))
        current_seats = fetch_seats(conn, account_id)

        # Reuse existing machine seat
        existing = next(
            (s for s in current_seats if s["machineId"] == machine_id), None
        )
        if existing:
            conn.execute(
                "UPDATE seats SET product_id = ? WHERE seat_id = ?",
                (product_id, existing["seatId"]),
            )
            existing["productId"] = product_id
            return {"approved": True, "reason": "existing_machine", "seat": existing}

        # Enforce seat cap
        if len(current_seats) >= max_seats:
            return {
                "approved": False,
                "reason": "seat_limit_reached",
                "maxSeats": max_seats,
            }

        # Create new seat
        seat_id = f"seat_{uuid.uuid4().hex[:10]}"
        conn.execute(
            "INSERT INTO seats (seat_id, account_id, machine_id, product_id) VALUES (?, ?, ?, ?)",
            (seat_id, account_id, machine_id, product_id),
        )
        seat = {
            "seatId": seat_id,
            "accountId": account_id,
            "machineId": machine_id,
            "productId": product_id,
            "status": "active",
        }
        return {"approved": True, "reason": "seat_assigned", "seat": seat}
