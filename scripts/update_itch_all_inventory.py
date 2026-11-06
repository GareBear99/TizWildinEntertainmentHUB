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

Media URLs are verified, not just collected: every cover/animated URL is
HEAD-checked during the refresh. A URL that 404s is replaced from the item's
current detail page (og:image / screenshots, first live candidate wins) and
the swap is recorded in the run report; a URL that still cannot be resolved
is flagged there instead of being silently kept. A URL that cannot be
checked (429 / 5xx / network error after retries) is "unknown" — never
treated as dead — so a rate-limit can never rewrite working media.
"""
from __future__ import annotations

import argparse
import html
import http.client
import json
import re
import subprocess
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


def fetch(url: str, timeout: int = 25, tries: int = 3, sleep_s: float = 0.8) -> str:
    last: Exception | None = None
    for attempt in range(tries):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
            return raw.decode("utf-8", errors="replace")
        except HTTPError as exc:
            last = exc
            # itch rate-limits aggressively (429) and sometimes resets the
            # connection mid-body (IncompleteRead). Back off longer on 429
            # (honour Retry-After when the server sends one) and retry.
            if exc.code == 429:
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                try:
                    wait = float(retry_after) if retry_after else 30.0
                except (TypeError, ValueError):
                    wait = 30.0
            else:
                wait = sleep_s
            if attempt + 1 < tries:
                time.sleep(wait)
        except (URLError, TimeoutError, http.client.HTTPException) as exc:
            last = exc
            if attempt + 1 < tries:
                time.sleep(sleep_s)
    # Last resort: itch resets urllib connections mid-body (IncompleteRead)
    # and rate-limits urllib harder than curl. curl ships on the GitHub
    # runner, macOS, and any normal Python host, so one curl attempt keeps a
    # transient transport failure from failing the whole refresh.
    try:
        return _fetch_curl(url, timeout)
    except Exception as exc:
        last = exc
    raise RuntimeError(f"failed to fetch {url}: {last}")


def _fetch_curl(url: str, timeout: int = 25) -> str:
    proc = subprocess.run(
        ["curl", "-sS", "--fail", "--max-time", str(timeout),
         "-A", USER_AGENT, "-H", "Accept: text/html,application/xhtml+xml", url],
        capture_output=True, timeout=timeout + 10)
    if proc.returncode != 0:
        raise RuntimeError(
            f"curl failed ({proc.returncode}): "
            f"{proc.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return proc.stdout.decode("utf-8", errors="replace")


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


def itch_original(url: str) -> str:
    """Normalize img.itch.zone URLs to the full-resolution 'original' variant.

    itch encodes a resize directive as the path segment after the base64 asset
    id (e.g. .../aW1n.../32x32%23/name.jpeg). Swapping that segment for
    'original' serves the same asset at the native resolution the itch listing
    displays, instead of whatever thumbnail variant the profile page exposed.
    """
    if not url or "img.itch.zone" not in url:
        return url
    return re.sub(r"(img\.itch\.zone/[^/]+/)[^/]+(/)", r"\1original\2", url, count=1)


def pick_media(urls: Iterable[str]) -> dict:
    urls = [itch_original(u) for u in urls if u]
    animated = next((u for u in urls if ".gif" in u.lower()), "")
    cover = next((u for u in urls if u != animated), "") or animated
    media_type = "gif" if animated else ("image" if cover else "fallback")
    return {"cover": cover, "animated": animated, "type": media_type}


_HEAD_CACHE: dict[str, str] = {}


def head_status(url: str, tries: int = 3) -> str:
    """Return 'live', 'dead', or 'unknown' for a media URL.

    HEAD first (no body, so itch's mid-body connection resets cannot bite);
    fall back to a ranged GET when HEAD is refused. 404/410 is dead.
    429/5xx/network errors are retried, then reported as unknown so a
    rate-limit never deletes or rewrites a working URL.
    """
    for attempt in range(tries):
        for method in ("HEAD", "GET"):
            try:
                req = Request(url, method=method, headers={"User-Agent": USER_AGENT})
                if method == "GET":
                    req.add_header("Range", "bytes=0-0")
                with urlopen(req, timeout=20) as resp:
                    if resp.status in (200, 206):
                        return "live"
                    if resp.status in (404, 410):
                        return "dead"
                    return "unknown"
            except HTTPError as exc:
                if exc.code in (404, 410):
                    return "dead"
                if exc.code in (429, 500, 502, 503, 504):
                    break  # retry the whole attempt
                return "unknown"
            except (URLError, TimeoutError, http.client.HTTPException):
                break  # retry the whole attempt
        if attempt + 1 < tries:
            time.sleep(2.0 * (attempt + 1))
    return "unknown"


def _head_cached(url: str) -> str:
    if url not in _HEAD_CACHE:
        _HEAD_CACHE[url] = head_status(url)
        time.sleep(0.1)
    return _HEAD_CACHE[url]


def pick_live_media(urls: Iterable[str]) -> dict:
    """Like pick_media, but skips URLs that do not resolve.

    Verifies candidates in priority order (og:image first) and picks the
    first live animated GIF and the first live cover. Dead candidates are
    counted and skipped. When nothing verifies live (e.g. the CDN is
    rate-limiting HEADs), falls back to the first unverified candidate so a
    transient outage never empties media — the caller records the
    verification state instead. Returns the media dict plus 'verified'
    ('live' | 'unknown' | 'dead') and 'dead_skipped'.
    """
    urls = [itch_original(u) for u in urls if u]
    ordered = list(dict.fromkeys(urls))
    live_gif = ""
    live_cover = ""
    unknown_gif = ""
    unknown_cover = ""
    dead_skipped = 0
    for u in ordered:
        status = _head_cached(u)
        if status == "dead":
            dead_skipped += 1
            continue
        is_gif = ".gif" in u.lower()
        if status == "live":
            if is_gif and not live_gif:
                live_gif = u
            elif not live_cover:
                live_cover = u
        else:  # unknown
            if is_gif and not unknown_gif:
                unknown_gif = u
            elif not unknown_cover:
                unknown_cover = u
        if live_gif and live_cover:
            break
    animated = live_gif or unknown_gif
    cover = live_cover or unknown_cover or animated
    if animated and cover:
        if _HEAD_CACHE.get(animated) == "live" and _HEAD_CACHE.get(cover) == "live":
            verified = "live"
        else:
            verified = "unknown"
    elif animated or cover:
        verified = "unknown"
    else:
        verified = "dead"
    media_type = "gif" if animated else ("image" if cover else "fallback")
    return {"cover": cover, "animated": animated, "type": media_type,
            "verified": verified, "dead_skipped": dead_skipped}


def parse_meta_media(page_html: str, base: str) -> list[str]:
    urls=[]
    # Attribute order varies (property before content and vice versa); match both
    # so the og:image full-resolution cover is never missed in favor of page thumbs.
    meta_res = [
        re.compile(r'''<meta[^>]+(?:property|name)=["'](?:og:image|twitter:image|twitter:image:src)["'][^>]+content=["']([^"']+)["'][^>]*>''', re.I),
        re.compile(r'''<meta[^>]+content=["']([^"']+)["'][^>]+(?:property|name)=["'](?:og:image|twitter:image|twitter:image:src)["'][^>]*>''', re.I),
    ]
    for meta_re in meta_res:
        for m in meta_re.finditer(page_html):
            u=abs_media_url(m.group(1), base)
            if is_media_like(u):
                urls.append(u)
    urls.extend(media_urls_from_html(page_html, base))
    seen=set(); out=[]
    for u in urls:
        u=itch_original(u)
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


def enrich_from_detail_page(item: dict) -> tuple[dict, str, dict]:
    url = item.get("url", "")
    if not url:
        return item, "no-url", {"verified": "dead", "dead_skipped": 0}
    try:
        body = fetch(url, tries=1)
    except Exception as exc:
        return item, f"detail-fetch-failed:{exc}", {"verified": "unknown", "dead_skipped": 0}
    media_urls = parse_meta_media(body, url)
    picked = pick_live_media(media_urls)
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
    return item, "ok", {"verified": picked["verified"], "dead_skipped": picked["dead_skipped"]}


def verify_and_repair_media(items: list[dict]) -> dict:
    """HEAD-verify every item's cover/animated; repair dead ones from the detail page.

    Runs after merge + enrich, so it also covers media that came from the
    profile page or survived a failed detail enrichment. A dead URL is
    replaced with the first live candidate from a fresh detail-page fetch;
    a URL that still cannot be resolved stays in place and is listed in
    'unresolved' (never silently kept). Returns the verification report.
    """
    repaired: list[dict] = []
    unresolved: list[dict] = []
    checked_urls = 0
    live_urls = 0
    dead_before = 0
    unverified_urls = 0
    media_ready = 0
    for item in items:
        media = item.setdefault("media", {})
        cover_status = _head_cached(media["cover"]) if media.get("cover") else "dead"
        animated_status = _head_cached(media["animated"]) if media.get("animated") else "dead"
        if media.get("cover"):
            checked_urls += 1
        if media.get("animated"):
            checked_urls += 1
        for status in (cover_status, animated_status):
            if status == "live":
                live_urls += 1
            elif status == "unknown":
                unverified_urls += 1
        dead_fields = [f for f, s in (("cover", cover_status), ("animated", animated_status))
                       if media.get(f) and s == "dead"]
        dead_before += len(dead_fields)
        if dead_fields:
            url = item.get("url", "")
            picked: dict = {}
            reason = ""
            if url:
                try:
                    body = fetch(url)
                    picked = pick_live_media(parse_meta_media(body, url))
                except Exception as exc:
                    reason = f"detail-refetch-failed:{exc}"
                time.sleep(0.5)
            else:
                reason = "no-url"
            for field in dead_fields:
                new = picked.get(field) or ""
                if new and new != media[field]:
                    repaired.append({"slug": item.get("id", ""), "field": field,
                                     "old": media[field], "new": new})
                    media[field] = new
                    media["source"] = "itch-detail"
                    media["updatedAt"] = now_iso()
                else:
                    unresolved.append({"slug": item.get("id", ""), "field": field,
                                       "url": media[field],
                                       "reason": reason or "no-live-media-on-detail-page"})
            media["type"] = "gif" if media.get("animated") else ("image" if media.get("cover") else "fallback")
        final_cover = _head_cached(media["cover"]) if media.get("cover") else "dead"
        final_animated = _head_cached(media["animated"]) if media.get("animated") else "dead"
        if final_cover == "live" or final_animated == "live":
            media_ready += 1
    return {
        "checkedUrls": checked_urls,
        "liveUrls": live_urls,
        "deadUrlsBeforeRepair": dead_before,
        "repairedCount": len(repaired),
        "unresolvedCount": len(unresolved),
        "unverifiedUrls": unverified_urls,
        "mediaReadyItems": media_ready,
        "repaired": repaired,
        "unresolved": unresolved,
    }


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
    enrich_dead_skipped = 0
    for scraped_item in scraped:
        slug=slug_from_url(scraped_item.get("url", ""))
        item=merge_item(existing_by_slug.get(slug), scraped_item, known_memberships)
        if enrich_details:
            item, status, note = enrich_from_detail_page(item)
            detail_status.append({"slug": slug, "status": status})
            enrich_dead_skipped += note.get("dead_skipped", 0)
            time.sleep(0.15)
        merged.append(item)
    # Preserve existing items not currently visible only if they are explicitly marked keep.
    scraped_slugs={slug_from_url(i.get("url", "")) for i in merged}
    extras=[i for i in manifest.get("items", []) if slug_from_url(i.get("url", "")) not in scraped_slugs and i.get("keepIfMissing")]
    merged.extend(extras)
    merged.sort(key=lambda x: x.get("rank", 999))
    media_check = verify_and_repair_media(merged)
    media_check["deadCandidatesSkippedDuringEnrich"] = enrich_dead_skipped
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
    # mediaReady now means "at least one media URL verified live", not just
    # "a URL string is present" — the old count was unverified.
    media_ready = media_check["mediaReadyItems"]
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
        "mediaVerification": {
            "checkedUrls": media_check["checkedUrls"],
            "liveUrls": media_check["liveUrls"],
            "deadUrlsBeforeRepair": media_check["deadUrlsBeforeRepair"],
            "deadCandidatesSkippedDuringEnrich": media_check["deadCandidatesSkippedDuringEnrich"],
            "repairedCount": media_check["repairedCount"],
            "unresolvedCount": media_check["unresolvedCount"],
            "unverifiedUrls": media_check["unverifiedUrls"],
        },
        "mediaRepaired": media_check["repaired"],
        "mediaUnresolved": media_check["unresolved"],
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
