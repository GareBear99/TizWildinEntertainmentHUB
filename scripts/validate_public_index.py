#!/usr/bin/env python3
"""Validate the generated public SEO index without requiring network access."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BASE = "https://garebear99.github.io/TizWildinEntertainmentHUB"
REQUIRED = ["docs/public-index.json", "docs/sitemap.xml", "docs/robots.txt", "docs/llms.txt", "docs/PUBLIC_LINK_GRAPH.md", "docs/ecosystem-index.html", "docs/arc-index.html"]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def check(cond: bool, msg: str) -> None:
    if not cond:
        fail(msg)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    for rel in REQUIRED:
        check((ROOT / rel).exists(), f"missing required file: {rel}")

    for rel in ["plugins.json", "packs.json", "lists.json", "docs/public-index.json", "docs/SEO_BUILD_REPORT.json", "docs/site.webmanifest"]:
        try:
            json.loads(read(ROOT / rel))
        except Exception as exc:
            fail(f"invalid JSON {rel}: {exc}")

    index = json.loads(read(DOCS / "public-index.json"))
    items = index.get("items", [])
    check(index.get("schemaVersion") == "2.0", "public-index schemaVersion must be 2.0")
    check(len(items) >= 50, f"expected at least 50 indexed items, found {len(items)}")

    ids = set()
    pages = set()
    canonicals = set()
    for item in items:
        for field in ["id", "name", "description", "cluster", "kind", "page", "pageUrl", "canonicalUrl"]:
            check(item.get(field), f"missing {field} for item {item.get('name')}")
        check(len(item["description"]) >= 40, f"description too short: {item['name']}")
        check(item["id"] not in ids, f"duplicate id: {item['id']}")
        ids.add(item["id"])
        pages.add(item["page"])
        canonicals.add(item["canonicalUrl"])
        page_path = DOCS / item["page"]
        check(page_path.exists(), f"missing item page: {item['page']}")
        html = read(page_path)
        for needle in ["<title>", "meta name=\"description\"", "rel=\"canonical\"", "application/ld+json", "og:title", "twitter:card"]:
            check(needle in html, f"{item['page']} missing {needle}")
        check(item["name"] in html, f"{item['page']} does not contain item name")

    # Parse sitemap and verify generated internal files exist locally.
    try:
        root = ET.parse(DOCS / "sitemap.xml").getroot()
    except Exception as exc:
        fail(f"sitemap parse failed: {exc}")
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [el.text for el in root.findall(".//sm:loc", ns) if el.text]
    check(len(locs) >= len(items), "sitemap should contain at least every item route")
    for page in pages:
        expected = f"{BASE}/{page}"
        check(expected in locs, f"sitemap missing item page: {expected}")
    for loc in locs:
        if loc.startswith(BASE):
            rel = loc[len(BASE):].lstrip("/")
            if rel == "":
                rel = "index.html"
            # Public root maps to docs/index.html in GitHub Pages.
            if rel.endswith("/"):
                rel += "index.html"
            check((DOCS / rel).exists(), f"sitemap local target missing: {rel}")

    # Check robots points to sitemap.
    robots = read(DOCS / "robots.txt")
    check(f"Sitemap: {BASE}/sitemap.xml" in robots, "robots.txt missing sitemap")

    # Guard against cache/dev artifacts in release package.
    bad = []
    for p in ROOT.rglob("*"):
        if any(part in {"__pycache__", ".pytest_cache", ".mypy_cache", ".DS_Store"} for part in p.parts):
            bad.append(str(p.relative_to(ROOT)))
        if p.suffix in {".pyc", ".pyo"}:
            bad.append(str(p.relative_to(ROOT)))
    check(not bad, "dev/cache artifacts present: " + ", ".join(bad[:20]))

    # Ensure linked route docs are not empty placeholder pages.
    graph = read(DOCS / "PUBLIC_LINK_GRAPH.md")
    check("FreeEQ8" in graph and "ARC-Core" in graph and "Public Credibility SEO Tracker" in graph, "link graph missing critical routes")

    print(f"VALIDATION OK: {len(items)} items, {len(locs)} sitemap URLs, {len(pages)} route pages")


if __name__ == "__main__":
    main()
