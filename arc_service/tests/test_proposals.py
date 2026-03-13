"""Tests for the /proposal endpoint."""


def test_install_missing_proposal(client):
    resp = client.post("/proposal", json={
        "proposalId": "p1",
        "type": "install_missing",
        "accountId": "demo_account",
        "machineId": "studio_mac",
        "requestedProducts": ["freeeq8", "therum"],
    })
    data = resp.json()
    assert data["approved"] is True
    assert len(data["actions"]) == 2
    for action in data["actions"]:
        assert action["action"] == "download_or_build"


def test_refresh_catalog_proposal(client):
    resp = client.post("/proposal", json={
        "proposalId": "p2",
        "type": "refresh_catalog",
        "accountId": "demo_account",
        "machineId": "studio_mac",
    })
    data = resp.json()
    assert data["approved"] is True
    assert "reload_catalog" in data["actions"]


def test_unknown_proposal_type(client):
    resp = client.post("/proposal", json={
        "proposalId": "p3",
        "type": "nuke_everything",
        "accountId": "demo_account",
        "machineId": "studio_mac",
    })
    data = resp.json()
    assert data["approved"] is False


def test_install_missing_free_only_account(client):
    """free_account requesting paid products should get purchase_required."""
    resp = client.post("/proposal", json={
        "proposalId": "p4",
        "type": "install_missing",
        "accountId": "free_account",
        "machineId": "laptop",
        "requestedProducts": ["therum", "freeeq8"],
    })
    data = resp.json()
    actions = {a["productId"]: a["action"] for a in data["actions"]}
    assert actions["therum"] == "purchase_required"
    assert actions["freeeq8"] == "download_or_build"
