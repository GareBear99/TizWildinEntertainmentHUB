"""Tests for seat assignment, reuse, and limit enforcement."""


def test_list_existing_seats(client):
    resp = client.get("/seats/demo_account")
    assert resp.status_code == 200
    seats = resp.json()
    assert len(seats) == 1
    assert seats[0]["machineId"] == "studio_mac"


def test_assign_new_seat(client):
    """demo_account has 2 extra seats (max 3 total) and 1 used — should succeed."""
    resp = client.post("/validate-runtime", json={
        "accountId": "demo_account",
        "machineId": "laptop_new",
        "productId": "freeeq8",
    })
    data = resp.json()
    assert data["approved"] is True
    assert data["seat"]["machineId"] == "laptop_new"


def test_existing_machine_reuse(client):
    """Hitting validate with the same machineId should reuse the existing seat."""
    resp = client.post("/validate-runtime", json={
        "accountId": "demo_account",
        "machineId": "studio_mac",
        "productId": "wurp",
    })
    data = resp.json()
    assert data["approved"] is True
    assert data["seat"]["machineId"] == "studio_mac"
    assert data["seat"]["productId"] == "wurp"


def test_seat_limit_enforcement(client):
    """free_account has 0 extra seats (max 1). Second machine should be rejected."""
    # First machine — ok
    client.post("/validate-runtime", json={
        "accountId": "free_account",
        "machineId": "machine_a",
        "productId": "freeeq8",
    })
    # Second machine — should fail
    resp = client.post("/validate-runtime", json={
        "accountId": "free_account",
        "machineId": "machine_b",
        "productId": "freeeq8",
    })
    data = resp.json()
    assert data["approved"] is False
    assert data["reason"] == "seat_limit_reached"
