"""Tests for the /catalog endpoint and catalog data integrity."""


def test_catalog_returns_all_products(client):
    resp = client.get("/catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert "products" in data
    assert len(data["products"]) == 13


def test_catalog_has_groups(client):
    data = client.get("/catalog").json()
    group_ids = [g["groupId"] for g in data["groups"]]
    assert "independent_headline_products" in group_ids
    assert "maid_suite" in group_ids
    assert "riftwave_suite" in group_ids


def test_every_product_has_repo_slug(client):
    data = client.get("/catalog").json()
    for p in data["products"]:
        assert "repoSlug" in p, f"{p['productId']} missing repoSlug"
        assert p["repoSlug"].startswith("GareBear99/")


def test_global_flags(client):
    data = client.get("/catalog").json()
    flags = data["globalFlags"]
    assert flags["maxExtraSeats"] == 9
    assert flags["extraSeatMonthlyPriceUsd"] == 3
