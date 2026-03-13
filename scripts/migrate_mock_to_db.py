#!/usr/bin/env python3
"""Seed the SQLite database from the existing mock JSON fixtures."""

import json
import sys
from pathlib import Path

# Ensure the app package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "arc_service"))

from app.db import init_db, get_db  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "arc_service" / "app" / "data"


def seed():
    init_db()

    ent_path = DATA_DIR / "entitlements.mock.json"
    seats_path = DATA_DIR / "seats.mock.json"

    entitlements: dict = json.loads(ent_path.read_text())
    seats: dict = json.loads(seats_path.read_text())

    with get_db() as conn:
        for account_id, ent in entitlements.items():
            conn.execute(
                """INSERT OR REPLACE INTO accounts
                   (account_id, owns_every_vst, extra_seat_qty, billing_state)
                   VALUES (?, ?, ?, ?)""",
                (
                    account_id,
                    int(ent.get("ownsEveryVST", False)),
                    ent.get("extraSeatQuantity", 0),
                    ent.get("billingState", "active"),
                ),
            )
            for pid in ent.get("ownedProducts", []):
                conn.execute(
                    "INSERT OR IGNORE INTO owned_products (account_id, product_id) VALUES (?, ?)",
                    (account_id, pid),
                )
            for bid in ent.get("ownedBundles", []):
                conn.execute(
                    "INSERT OR IGNORE INTO owned_bundles (account_id, bundle_id) VALUES (?, ?)",
                    (account_id, bid),
                )

        for account_id, seat_list in seats.items():
            for s in seat_list:
                conn.execute(
                    """INSERT OR REPLACE INTO seats
                       (seat_id, account_id, machine_id, product_id, status)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        s["seatId"],
                        s["accountId"],
                        s["machineId"],
                        s["productId"],
                        s.get("status", "active"),
                    ),
                )

    print(f"Seeded {len(entitlements)} account(s) and {sum(len(v) for v in seats.values())} seat(s).")


if __name__ == "__main__":
    seed()
