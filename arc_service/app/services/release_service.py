"""
GitHub release polling service.

Queries the GitHub Releases API for each product repo and returns
the latest tag, published date, and downloadable assets.
"""

import os
import httpx
from app.services.catalog_service import load_catalog

GITHUB_API = "https://api.github.com"
# Optional: set GITHUB_TOKEN env var for higher rate limits on public repos
_TOKEN = os.environ.get("GITHUB_TOKEN")
_HEADERS = {"Accept": "application/vnd.github+json"}
if _TOKEN:
    _HEADERS["Authorization"] = f"Bearer {_TOKEN}"


def _repo_slug_for(product_id: str) -> str | None:
    catalog = load_catalog()
    product = next(
        (p for p in catalog["products"] if p["productId"] == product_id), None
    )
    return product.get("repoSlug") if product else None


def get_latest_release(product_id: str) -> dict:
    """Return the latest GitHub release for a single product."""
    slug = _repo_slug_for(product_id)
    if not slug:
        return {"productId": product_id, "error": "no_repo_slug"}

    url = f"{GITHUB_API}/repos/{slug}/releases/latest"
    try:
        resp = httpx.get(url, headers=_HEADERS, timeout=10)
        if resp.status_code == 404:
            return {"productId": product_id, "tag": None, "message": "no_releases"}
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        return {"productId": product_id, "error": str(exc)}

    data = resp.json()
    assets = [
        {"name": a["name"], "size": a["size"], "download_url": a["browser_download_url"]}
        for a in data.get("assets", [])
    ]
    return {
        "productId": product_id,
        "repoSlug": slug,
        "tag": data.get("tag_name"),
        "name": data.get("name"),
        "publishedAt": data.get("published_at"),
        "assets": assets,
        "htmlUrl": data.get("html_url"),
    }


def bulk_release_check() -> list[dict]:
    """Check every product with a repoSlug for its latest release."""
    catalog = load_catalog()
    results = []
    seen_slugs: dict[str, dict] = {}  # avoid duplicate API calls for shared repos

    for product in catalog["products"]:
        slug = product.get("repoSlug")
        if not slug:
            continue

        if slug in seen_slugs:
            # Shared repo (e.g. RiftWave suite) — reuse the cached result
            cached = seen_slugs[slug].copy()
            cached["productId"] = product["productId"]
            results.append(cached)
            continue

        info = get_latest_release(product["productId"])
        seen_slugs[slug] = info
        results.append(info)

    return results
