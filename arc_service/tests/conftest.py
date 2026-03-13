"""Shared fixtures for ARC service tests."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure the arc_service package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(autouse=True)
def _use_temp_db(tmp_path, monkeypatch):
    """Point every test at an isolated SQLite database."""
    db_file = tmp_path / "test_arc.db"
    monkeypatch.setattr("app.db.DB_PATH", db_file)
    from app.db import init_db
    init_db()
    yield


@pytest.fixture()
def seed_demo(tmp_path):
    """Seed the temp DB with demo + free accounts."""
    from app.db import get_db
    with get_db() as conn:
        conn.execute(
            "INSERT INTO accounts (account_id, owns_every_vst, extra_seat_qty, billing_state) VALUES (?, ?, ?, ?)",
            ("demo_account", 1, 2, "active"),
        )
        conn.execute(
            "INSERT INTO owned_bundles (account_id, bundle_id) VALUES (?, ?)",
            ("demo_account", "complete_collection"),
        )
        conn.execute(
            "INSERT INTO accounts (account_id, owns_every_vst, extra_seat_qty, billing_state) VALUES (?, ?, ?, ?)",
            ("free_account", 0, 0, "active"),
        )
        conn.execute(
            "INSERT INTO accounts (account_id, owns_every_vst, extra_seat_qty, billing_state) VALUES (?, ?, ?, ?)",
            ("broke_account", 0, 0, "payment_issue"),
        )
        conn.execute(
            "INSERT INTO owned_products (account_id, product_id) VALUES (?, ?)",
            ("broke_account", "therum"),
        )
        conn.execute(
            "INSERT INTO seats (seat_id, account_id, machine_id, product_id) VALUES (?, ?, ?, ?)",
            ("seat_demo_001", "demo_account", "studio_mac", "therum"),
        )


@pytest.fixture()
def client(seed_demo):
    """A TestClient against the FastAPI app with seeded data."""
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as c:
        yield c
