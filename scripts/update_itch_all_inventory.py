#!/usr/bin/env python3
"""Refresh GareBearProductionz itch inventory and media into all_items.json.

This is intentionally stdlib-only so it can run inside GitHub Actions, a Mac
Terminal, or any Python 3 install without dependency setup.

Why build-time instead of browser-time?
- The HUB is a static GitHub Pages site.
- Browsers commonly block direct client-side scraping of itch.io HTML via CORS.
- The rest of this HUB already uses no-cache JSON manifests as the live source.

So this script pulls the public itch pages, writes the manifest, and the site then
loads all_items.json with cache busting just like plugins.json/packs.json/etc.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROFILE_URL = "https://garebearproductionz.itch.io/"
ACCOUNT_HOST = "garebearproductionz.itch.io"
MANIFEST_PATH = ROOT / "all_items.json"
DOCS_DATA_PATH = ROOT / "docs" / "data" / "all_items.json"
REPORT_PATH = ROOT / "docs" / "ITCH_AUTOPULL_REPORT.json"
SELLER_PAGE_PATHS = [ROOT / "all-account-inventory.html", ROOT / "docs" / "pages" / "all-account-inventory.html"]
TSV_PATH = ROOT / "ALL_ACCOUNT_INVENTORY.tsv"
USER_AGENT = "Mozilla/5.0 (compatible; GareBearProductionz-HUB-InventoryBot/1.0; +https://garebear99.github.io/TizWildinEntertainmentHUB/)"

# Slugs that are storefront constructs rather than individual products get a
# dedicated kind so downstream consumers can treat them separately.
BUNDLE_SLUGS = {"bundle"}

# Ordered most-specific-first. Generic catch-alls like bare "engine" were
# removed from game_tools because they swallowed dice packs, backdrops, and
# playable engines into the wrong bucket.
CATEGORY_RULES = [
    ("audio_music", ["audio", "sfx", "violin", "eq", "theme", "npc", "synth formula", "sound"]),
    ("wraith_lore", ["wraith", "comic", "cathedral", "darkhold", "necropolis", "jukebox", "nekranomicon"]),
    ("icons_sigils", ["icon", "sigil", "covenant", "holy", "spectral", "hell", "evil eye"]),
    ("live_backdrops", ["backdrop", "sphinx", "alien", "mountain", "sky", "crawl space", "sunset", "gate", "live map", "scene"]),
    ("weapons_props", ["hammer", "mjolnir", "scythe", "device", "cart", "paladin", "teleportation", "prop", "dice", "d20", "coin"]),
    ("hero_generators", ["laser", "fireball", "sprite fusion", "sprite mutation", "combat timeline", "moon", "generator engine"]),
    ("sprite_characters", ["sprite", "sprites", "haunter", "demon", "chibi", "pyro", "skully", "elemental", "character", "portrait"]),
    ("games_engines", ["neolution", "grid", "controller", "game", "canvas", "mode-7", "floorcast", "ray trace", "raycast", "ray cast", "playable"]),
    ("game_tools", ["formula", "timeline", "metadata", "action command", "reward pocket", "projectile", "pentagram", "converter", "exporter", "physics", "fx engine", "overlay engine", "toolkit", "engine"]),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch(url: str, timeout: int = 25, tries: int = 2, sleep_s: float = 0.8) -> str:
    last: Exception | None = None
    for attempt in range(tries):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
            return raw.decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError) as exc:
            last = exc
            if attempt + 1 < tries:
                time.sleep(sleep_s)
    raise RuntimeError(f"failed to fetch {url}: {last}")


def clean_text(s: str) -> str:
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return " ".join(s.split())


def slug_from_url(url: str) -> str:
    return urlparse(url).path.strip("/").split("/")[-1]


def item_id_from_name_or_url(name: str, url: str) -> str:
    slug = slug_from_url(url)
    if slug:
        return slug
    raw = name.lower().replace("+", " plus ").replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", raw).strip("-") or "itch-item"


def abs_media_url(url: str, base: str = PROFILE_URL) -> str:
    url = html.unescape(url or "").strip()
    if not url or url.startswith("data:"):
        return ""
    if url.startswith("//"):
        return "https:" + url
    return urljoin(base, url)


def media_urls_from_html(block: str, base: str) -> list[str]:
    urls: list[str] = []
    # Common itch attrs: src, data-lazy_src, data-lazy-src, href on screenshot/GIF links,
    # srcset candidates, and background-image:url(...).
    attr_re = re.compile(r'''(?:src|href|data-lazy_src|data-lazy-src|data-background_image|poster)\s*=\s*["']([^"']+)["']''', re.I)
    for m in attr_re.finditer(block):
        u = abs_media_url(m.group(1), base)
        if is_media_like(u):
            urls.append(u)
    for m in re.finditer(r'''srcset\s*=\s*["']([^"']+)["']''', block, flags=re.I):
        for part in m.group(1).split(','):
            u = abs_media_url(part.strip().split(' ')[0], base)
            if is_media_like(u):
                urls.append(u)
    for m in re.finditer(r'''url\(([^)]+)\)''', block, flags=re.I):
        u = abs_media_url(m.group(1).strip('"\''), base)
        if is_media_like(u):
            urls.append(u)
    # Deduplicate while preserving order.
    out=[]
    seen=set()
    for u in urls:
        if u not in seen:
            out.append(u); seen.add(u)
    return out


def is_media_like(url: str) -> bool:
    if not url:
        return False
    lower = url.lower()
    if any(ext in lower for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif"]):
        return True
    # itch image CDN sometimes has resizing paths without obvious extensions.
    if "img.itch.zone" in lower or "uploads2.itch.io" in lower:
        return True
    return False


def pick_media(urls: Iterable[str]) -> dict:
    urls = [u for u in urls if u]
    animated = next((u for u in urls if ".gif" in u.lower()), "")
    cover = next((u for u in urls if u != animated), "") or animated
    media_type = "gif" if animated else ("image" if cover else "fallback")
    return {"cover": cover, "animated": animated, "type": media_type}


def parse_meta_media(page_html: str, base: str) -> list[str]:
    urls=[]
    meta_re = re.compile(r'''<meta[^>]+(?:property|name)=["'](?:og:image|twitter:image|twitter:image:src)["'][^>]+content=["']([^"']+)["'][^>]*>''', re.I)
    for m in meta_re.finditer(page_html):
        u=abs_media_url(m.group(1), base)
        if is_media_like(u):
            urls.append(u)
    urls.extend(media_urls_from_html(page_html, base))
    seen=set(); out=[]
    for u in urls:
        if u not in seen:
            out.append(u); seen.add(u)
    return out


def split_profile_item_blocks(profile_html: str) -> list[str]:
    # Keep only creator-owned product grid above Supported/Collections so we do not ingest supported products.
    cut_points = [
        profile_html.lower().find("supported by garebearproductionz"),
        profile_html.lower().find("garebearproductionz's collection"),
    ]
    cuts = [x for x in cut_points if x > 0]
    if cuts:
        profile_html = profile_html[:min(cuts)]
    # Prefer itch game_cell chunks, fallback to coarse chunks around account item links.
    parts = re.split(r'(?=<div[^>]+class=["\'][^"\']*(?:game_cell|game_cell_data|game_grid_cell)[^"\']*["\'])', profile_html, flags=re.I)
    blocks = [p for p in parts if ACCOUNT_HOST in p and "href=" in p]
    if blocks:
        return blocks
    # Fallback: anchor-centered windows.
    out=[]
    for m in re.finditer(r'href=["\'](https://garebearproductionz\.itch\.io/[^"\'#?]+)[^"\']*["\']', profile_html, re.I):
        lo=max(0, m.start()-1200); hi=min(len(profile_html), m.end()+2400)
        out.append(profile_html[lo:hi])
    return out


def parse_item_block(block: str, rank: int) -> dict | None:
    links = re.findall(r'''<a[^>]+href=["'](https://garebearproductionz\.itch\.io/[^"'#?]+)[^"']*["'][^>]*>([\s\S]*?)</a>''', block, flags=re.I)
    candidates=[]
    for url, inner in links:
        slug=slug_from_url(url)
        if not slug or slug in {"", "community"}:
            continue
        title=clean_text(inner)
        # Skip author/profile/follow links and image-only anchors.
        if not title or title.lower() in {"garebearproductionz", "follow", "collection", "add to collection", "image", "gif"}:
            continue
        if title.startswith("$") or len(title) < 3:
            continue
        candidates.append((url, title))
    if not candidates:
        return None
    url, title = candidates[0]
    slug=slug_from_url(url)
    text=clean_text(block)
    # Description is best-effort: remove repeated title/author/price fragments and trim.
    desc=text.replace(title, " ").replace("GareBearProductionz", " ")
    desc=re.sub(r"\$\d+(?:\.\d+)?(?:\s*-\d+%)?", " ", desc)
    desc=" ".join(desc.split())
    if len(desc) > 220:
        desc = desc[:219].rsplit(" ",1)[0] + "…"
    price_type = "free" if re.search(r"\bfree\b|name your own price", text, flags=re.I) or "(FREE" in title.upper() else "paid"
    media = pick_media(media_urls_from_html(block, PROFILE_URL))
    return {
        "id": slug,
        "rank": rank,
        "name": title,
        "url": url,
        "description": desc,
        "priceType": price_type,
        "media": {
            **media,
            "alt": title,
            "source": "itch-profile",
            "updatedAt": now_iso(),
        },
        "itch": {"slug": slug, "priceLabel": extract_price_label(text), "creator": "GareBearProductionz", "lastSeenOnProfile": now_iso()},
    }


def extract_price_label(text: str) -> str:
    m = re.search(r"(?:FREE|Free|\$\d+(?:\.\d+)?(?:\s*-\d+%)?)", text)
    return m.group(0) if m else ""


def infer_category(name: str, default: str = "game_tools") -> str:
    low=name.lower()
    for cat, terms in CATEGORY_RULES:
        if any(t in low for t in terms):
            return cat
    if "free" in low:
        return "free_samples"
    return default


def merge_item(existing: dict | None, scraped: dict, known_sale_memberships: dict[str, list[str]]) -> dict:
    merged = dict(existing or {})
    merged.update({
        "id": existing.get("id") if existing else scraped["id"],
        "rank": scraped.get("rank") or (existing or {}).get("rank", 999),
        "name": scraped.get("name") or (existing or {}).get("name", ""),
        "url": scraped.get("url") or (existing or {}).get("url", ""),
        "priceType": scraped.get("priceType") or (existing or {}).get("priceType", "paid"),
        "status": (existing or {}).get("status", "released"),
        "accountOwner": "GareBearProductionz",
        "source": PROFILE_URL,
    })
    if not merged.get("category"):
        merged["category"] = infer_category(merged.get("name", ""))
    slug_now = slug_from_url(merged.get("url", ""))
    if slug_now in BUNDLE_SLUGS:
        merged["kind"] = "bundle"
    elif not merged.get("kind"):
        merged["kind"] = "tool" if merged["category"] in {"game_tools", "hero_generators"} else "asset_pack"
    # Preserve hand-written descriptions unless the scraped one is more useful.
    if not merged.get("description") or len(merged.get("description", "")) < 30:
        merged["description"] = scraped.get("description", "")
    merged.setdefault("tags", [])
    merged.setdefault("featured", False)
    memberships = set(merged.get("saleMemberships") or [])
    memberships.update(known_sale_memberships.get(slug_from_url(merged.get("url", "")), []))
    merged["saleMemberships"] = sorted(memberships)
    old_media = merged.get("media") or {}
    new_media = scraped.get("media") or {}
    # Prefer animated media, then explicit cover, but do not erase known working URLs.
    merged["media"] = {
        "cover": new_media.get("cover") or old_media.get("cover", ""),
        "animated": new_media.get("animated") or old_media.get("animated", ""),
        "type": "gif" if (new_media.get("animated") or old_media.get("animated")) else ("image" if (new_media.get("cover") or old_media.get("cover")) else "fallback"),
        "alt": merged.get("name", "GareBearProductionz itch item cover"),
        "source": new_media.get("source") or old_media.get("source", "pending-autopull"),
        "updatedAt": now_iso(),
    }
    itch = dict(merged.get("itch") or {})
    itch.update(scraped.get("itch") or {})
    itch.setdefault("slug", slug_from_url(merged.get("url", "")))
    itch.setdefault("creator", "GareBearProductionz")
    merged["itch"] = itch
    return merged


def scrape_sale_memberships(sales: list[dict]) -> dict[str, list[str]]:
    memberships: dict[str, list[str]] = {}
    for sale in sales:
        sale_id = sale.get("id") or "sale"
        url = sale.get("url")
        if not url:
            continue
        try:
            body = fetch(url, tries=1)
        except Exception as exc:
            print(f"warn: could not scrape sale {url}: {exc}", file=sys.stderr)
            continue
        for m in re.finditer(r'href=["\'](https://garebearproductionz\.itch\.io/[^"\'#?]+)[^"\']*["\']', body, re.I):
            slug = slug_from_url(m.group(1))
            memberships.setdefault(slug, [])
            if sale_id not in memberships[slug]:
                memberships[slug].append(sale_id)
    return memberships


def enrich_from_detail_page(item: dict) -> tuple[dict, str]:
    url = item.get("url", "")
    if not url:
        return item, "no-url"
    try:
        body = fetch(url, tries=1)
    except Exception as exc:
        return item, f"detail-fetch-failed:{exc}"
    media_urls = parse_meta_media(body, url)
    picked = pick_media(media_urls)
    media = item.setdefault("media", {})
    if picked.get("animated"):
        media["animated"] = picked["animated"]
    if picked.get("cover"):
        media["cover"] = picked["cover"]
    media["type"] = "gif" if media.get("animated") else ("image" if media.get("cover") else "fallback")
    media["source"] = "itch-detail"
    media["alt"] = item.get("name", "GareBearProductionz itch item cover")
    media["updatedAt"] = now_iso()
    # Capture updated/published text if present without being too brittle.
    text = clean_text(body)
    itch = item.setdefault("itch", {})
    for label in ["Published", "Updated"]:
        m = re.search(label + r"\s+([^\n\r]{0,80}?)(?:Status|Category|Author|Tags|Purchase|$)", text, re.I)
        if m:
            itch[label.lower()] = " ".join(m.group(1).split())[:80]
    return item, "ok"


def update_manifest(enrich_details: bool = True, limit: int | None = None) -> tuple[dict, dict]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    sales = manifest.get("sales", [])
    known_memberships = scrape_sale_memberships(sales)
    profile_html = fetch(PROFILE_URL)
    blocks = split_profile_item_blocks(profile_html)
    scraped=[]
    seen=set()
    rank=1
    for block in blocks:
        item=parse_item_block(block, rank)
        if not item:
            continue
        slug=item["id"]
        if slug in seen:
            continue
        seen.add(slug)
        scraped.append(item)
        rank += 1
        if limit and len(scraped)>=limit:
            break
    existing_by_slug={slug_from_url(i.get("url", "")): i for i in manifest.get("items", [])}
    merged=[]
    detail_status=[]
    for scraped_item in scraped:
        slug=slug_from_url(scraped_item.get("url", ""))
        item=merge_item(existing_by_slug.get(slug), scraped_item, known_memberships)
        if enrich_details:
            item, status = enrich_from_detail_page(item)
            detail_status.append({"slug": slug, "status": status})
            time.sleep(0.15)
        merged.append(item)
    # Preserve existing items not currently visible only if they are explicitly marked keep.
    scraped_slugs={slug_from_url(i.get("url", "")) for i in merged}
    extras=[i for i in manifest.get("items", []) if slug_from_url(i.get("url", "")) not in scraped_slugs and i.get("keepIfMissing")]
    merged.extend(extras)
    merged.sort(key=lambda x: x.get("rank", 999))
    manifest["items"] = merged
    manifest.setdefault("metadata", {})
    manifest["metadata"].update({
        "generatedAt": now_iso(),
        "autopullLastRun": now_iso(),
        "autopullSource": PROFILE_URL,
        "autopullItemCount": len(merged),
        "autopullDetailEnriched": bool(enrich_details),
    })
    manifest["generatedAt"] = now_iso()
    paid=sum(1 for i in merged if i.get("priceType") == "paid")
    free=sum(1 for i in merged if i.get("priceType") == "free")
    media_ready=sum(1 for i in merged if (i.get("media") or {}).get("cover") or (i.get("media") or {}).get("animated"))
    manifest.setdefault("summary", {})
    manifest["summary"].update({
        "totalItems": len(merged),
        "totalPublicProfileItems": len(scraped),
        "paidItems": paid,
        "freeItems": free,
        "mediaReadyItems": media_ready,
        "autopullReady": True,
    })
    # Refresh sale item counts from current memberships.
    for sale in manifest.get("sales", []):
        sid=sale.get("id")
        if sid:
            sale["itemCount"] = sum(1 for i in merged if sid in (i.get("saleMemberships") or []))
    report={
        "generatedAt": now_iso(),
        "profileUrl": PROFILE_URL,
        "itemsParsed": len(scraped),
        "itemsWritten": len(merged),
        "mediaReadyItems": media_ready,
        "detailStatus": detail_status[:200],
    }
    return manifest, report


def bake_seller_page(manifest: dict) -> list[str]:
    """Re-embed the manifest into the static buyer/crawler landing page.

    The page keeps a baked `const MANIFEST = {...};` so it works with zero
    fetches and stays crawler-readable; this replaces that snapshot with the
    freshly pulled inventory on every autopull run.
    """
    payload = json.dumps(manifest, ensure_ascii=False)
    payload = payload.replace("</", "<\\/")  # keep </script> impossible inside the inline block
    baked: list[str] = []
    for path in SELLER_PAGE_PATHS:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        new_text, n = re.subn(r"const MANIFEST = .*;\n", f"const MANIFEST = {payload};\n", text, count=1)
        if n != 1:
            print(f"warn: MANIFEST block not found in {path}", file=sys.stderr)
            continue
        path.write_text(new_text, encoding="utf-8")
        baked.append(str(path.relative_to(ROOT)))
    return baked


def bake_tsv(manifest: dict) -> None:
    rows = ["rank\tid\ttitle\tcategory\tpriceType\tkind\tsales\turl"]
    for i in sorted(manifest.get("items", []), key=lambda x: x.get("rank", 999)):
        rows.append("\t".join([
            str(i.get("rank", "")),
            i.get("id", ""),
            i.get("name", "").replace("\t", " "),
            i.get("category", ""),
            i.get("priceType", ""),
            i.get("kind", ""),
            ",".join(i.get("saleMemberships") or []),
            i.get("url", ""),
        ]))
    TSV_PATH.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> int:
    ap=argparse.ArgumentParser(description="Refresh all_items.json from public GareBearProductionz itch inventory.")
    ap.add_argument("--no-detail", action="store_true", help="Do not fetch each product page for og:image/screenshot/GIF enrichment.")
    ap.add_argument("--limit", type=int, default=None, help="Debug limit for number of profile items to process.")
    ap.add_argument("--bake-only", action="store_true", help="Skip network scraping; rebake the seller page and TSV from the existing all_items.json.")
    args=ap.parse_args()
    if args.bake_only:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        baked = bake_seller_page(manifest)
        bake_tsv(manifest)
        print(f"bake-only: refreshed {', '.join(baked) or 'no seller pages'} and {TSV_PATH.name} from existing manifest ({len(manifest.get('items', []))} items)")
        return 0
    manifest, report = update_manifest(enrich_details=not args.no_detail, limit=args.limit)
    text=json.dumps(manifest, indent=2, ensure_ascii=False)+"\n"
    MANIFEST_PATH.write_text(text, encoding="utf-8")
    DOCS_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_DATA_PATH.write_text(text, encoding="utf-8")
    baked = bake_seller_page(manifest)
    bake_tsv(manifest)
    report["sellerPagesBaked"] = baked
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(f"wrote {MANIFEST_PATH} with {report['itemsWritten']} items; media ready {report['mediaReadyItems']}; baked {len(baked)} seller pages + TSV")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
