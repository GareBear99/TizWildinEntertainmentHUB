"""
SQLite persistence layer for TizWildin Hub ARC.

Replaces the mock JSON files with a real database while keeping
the catalog manifest as a static JSON file (it's config, not user data).
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent / "data" / "arc.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    account_id     TEXT PRIMARY KEY,
    owns_every_vst INTEGER NOT NULL DEFAULT 0,
    extra_seat_qty INTEGER NOT NULL DEFAULT 0 CHECK(extra_seat_qty BETWEEN 0 AND 9),
    billing_state  TEXT    NOT NULL DEFAULT 'active',
    created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS owned_products (
    account_id TEXT NOT NULL REFERENCES accounts(account_id),
    product_id TEXT NOT NULL,
    PRIMARY KEY (account_id, product_id)
);

CREATE TABLE IF NOT EXISTS owned_bundles (
    account_id TEXT NOT NULL REFERENCES accounts(account_id),
    bundle_id  TEXT NOT NULL,
    PRIMARY KEY (account_id, bundle_id)
);

CREATE TABLE IF NOT EXISTS seats (
    seat_id    TEXT PRIMARY KEY,
    account_id TEXT NOT NULL REFERENCES accounts(account_id),
    machine_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS receipts (
    receipt_id        TEXT PRIMARY KEY,
    account_id        TEXT NOT NULL REFERENCES accounts(account_id),
    stripe_event_id   TEXT UNIQUE,
    stripe_event_type TEXT,
    product_id        TEXT,
    amount_cents      INTEGER,
    currency          TEXT DEFAULT 'usd',
    payload           TEXT,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    """Yield a sqlite3 connection that auto-commits on success."""
    conn = _get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create all tables if they don't exist."""
    with get_db() as conn:
        conn.executescript(SCHEMA)


# ---------------------------------------------------------------------------
# Convenience helpers used by the service layer
# ---------------------------------------------------------------------------

def fetch_account(conn: sqlite3.Connection, account_id: str) -> dict | None:
    row = conn.execute(
        "SELECT * FROM accounts WHERE account_id = ?", (account_id,)
    ).fetchone()
    if not row:
        return None

    products = [
        r["product_id"]
        for r in conn.execute(
            "SELECT product_id FROM owned_products WHERE account_id = ?",
            (account_id,),
        )
    ]
    bundles = [
        r["bundle_id"]
        for r in conn.execute(
            "SELECT bundle_id FROM owned_bundles WHERE account_id = ?",
            (account_id,),
        )
    ]
    return {
        "accountId": row["account_id"],
        "ownsEveryVST": bool(row["owns_every_vst"]),
        "ownedProducts": products,
        "ownedBundles": bundles,
        "extraSeatQuantity": row["extra_seat_qty"],
        "billingState": row["billing_state"],
    }


def fetch_seats(conn: sqlite3.Connection, account_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM seats WHERE account_id = ?", (account_id,)
    ).fetchall()
    return [
        {
            "seatId": r["seat_id"],
            "accountId": r["account_id"],
            "machineId": r["machine_id"],
            "productId": r["product_id"],
            "status": r["status"],
        }
        for r in rows
    ]
