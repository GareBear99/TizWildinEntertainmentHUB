"""Tests for entitlement resolution and the /entitlements endpoint."""


def test_get_demo_entitlement(client):
    resp = client.get("/entitlements/demo_account")
    assert resp.status_code == 200
    data = resp.json()
    assert data["accountId"] == "demo_account"
    assert data["ownsEveryVST"] is True
    assert data["extraSeatQuantity"] == 2


def test_get_free_entitlement(client):
    resp = client.get("/entitlements/free_account")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ownsEveryVST"] is False
    assert data["ownedProducts"] == []


def test_unknown_account_404(client):
    resp = client.get("/entitlements/nonexistent")
    assert resp.status_code == 404


def test_free_product_always_allowed(client):
    """FreeEQ8 is FREE_OPEN — even free_account can access it."""
    resp = client.post("/validate-runtime", json={
        "accountId": "free_account",
        "machineId": "laptop_1",
        "productId": "freeeq8",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["approved"] is True
    assert data["reason"] == "free_access"


def test_complete_collection_grants_pro(client):
    """demo_account owns everything — should get pro access to paid plugins."""
    resp = client.post("/validate-runtime", json={
        "accountId": "demo_account",
        "machineId": "studio_mac",
        "productId": "therum",
    })
    data = resp.json()
    assert data["approved"] is True
    assert "pro" in data["features"]


def test_payment_issue_blocks_paid_product(client):
    """broke_account owns therum but has payment_issue — should be blocked."""
    resp = client.post("/validate-runtime", json={
        "accountId": "broke_account",
        "machineId": "laptop_2",
        "productId": "therum",
    })
    data = resp.json()
    assert data["approved"] is False
    assert data["reason"] == "payment_issue"


def test_free_product_still_works_with_payment_issue(client):
    """Even with billing problems, free products should work."""
    resp = client.post("/validate-runtime", json={
        "accountId": "broke_account",
        "machineId": "laptop_2",
        "productId": "freeeq8",
    })
    data = resp.json()
    assert data["approved"] is True


def test_unknown_product(client):
    resp = client.post("/validate-runtime", json={
        "accountId": "demo_account",
        "machineId": "studio_mac",
        "productId": "does_not_exist",
    })
    data = resp.json()
    assert data["approved"] is False
    assert data["reason"] == "unknown_product"
