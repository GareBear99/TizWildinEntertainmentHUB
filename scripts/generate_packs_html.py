#!/usr/bin/env python3
"""Generate packs.html from packs.json (root is the source of truth).

Replaces the hand-written static packs.html that build_public_index.py
used to call out ("hand-written static page"). The pack catalog — cards,
tag lists, and the JSON-LD CreativeWork entries — is now generated from
packs.json, so a packs.json change can no longer drift from the page.

What is generated from packs.json:
  * the two catalog sections (TizWildin packs, then producer kits), in
    packs.json order, with name / description / tags / GitHub link per
    pack, and the "Pack page" slug derived from the pack name;
  * the JSON-LD CollectionPage (descriptions straight from packs.json,
    keywords = display tags + "sample-pack, producer-tools");
  * the hero eyebrow count and the 13 / 5 / 8 stat numbers.

What is NOT generated from packs.json (deliberate, documented):
  * the itch row: a dated inventory snapshot ("Prices as listed on itch
    (inventory snapshot 2026-11-06)") whose prices have already moved
    on from all_items.json (11 chips differ from it, e.g. Orc Bungalo
    $5.50 on the page vs a stale $2.75 -50% label in all_items.json).
    The generator preserves that section verbatim from the existing
    packs.html on disk and refuses to run if the file (and its itch
    row) is missing, rather than inventing prices. Refreshing the row
    is the itch-inventory workflow's job, not this script's.
  * prose counts in the meta description / lead ("13 free sample
    packs...") stay static text; only the eyebrow + stat numbers are
    computed.

Display overrides — pack data as published differs from packs.json in
three known, pre-existing places (the hand-written page drifted from
the JSON). These are recorded here explicitly instead of silently
baking the drift into the template, so a future packs.json fix can
delete the override:
  * DISPLAY_DESCRIPTION: round 2 added the "free 808 sample pack"
    SEO line to the 808 card only; packs.json keeps the plain text.
  * DISPLAY_TAGS: the Phonk and Future Bass cards show tags the JSON
    does not have (phonk: 808/cowbell/midi, not drift/starter;
    future-bass: loops/drums/synths, i.e. drums added).
  * ITCH_LINKS: only Violin, 808, and Subwoofer Crown have itch
    listings; the rest are GitHub-only until published (per the itch
    inventory report, Drum / Riser / Dark Piano / Future Bass /
    Phonk are prepped but not published on itch yet).
  * SUBWOOFER_NOTE: the "no separate Subwoofer Crown repo" note on
    that card only.

Featured packs: a pack with "featured": true in packs.json gets
class "item featured" and a green "⭐ Featured" badge as its first
tag. (Same field name as all_items.json's per-item "featured".)

Usage:
  python3 scripts/generate_packs_html.py            # write packs.html + docs/packs.html
  python3 scripts/generate_packs_html.py --check    # exit 1 + diff if output differs
"""

import argparse
import difflib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS_JSON = ROOT / "packs.json"
PACKS_HTML = ROOT / "packs.html"
DOCS_HTML = ROOT / "docs" / "packs.html"
BASE = "https://garebear99.github.io/TizWildinEntertainmentHUB"
GITHUB = "https://github.com/GareBear99"

# --- display overrides (see module docstring) ---------------------------
DISPLAY_DESCRIPTION = {
    # Round 2 (2026-11-08): "free 808 sample pack" SEO line, card only.
    "free_808_producer": "A free 808 sample pack — 94 hand-crafted 808 bass samples tuned to every chromatic key.",
}
DISPLAY_TAGS = {
    # Card/JSON-LD tags as published; packs.json still says otherwise.
    "phonk_producer": ["phonk", "808", "cowbell", "midi"],
    "free_future_bass": ["future-bass", "loops", "drums", "synths"],
}
ITCH_LINKS = {
    "free_violin_synth": "https://garebearproductionz.itch.io/violin-synth-sample-kit",
    "free_808_producer": "https://garebearproductionz.itch.io/808-producer-kit",
    "subwoofer_crown_bass": "https://garebearproductionz.itch.io/subwoofer-crown-bass-pack",
}
SUBWOOFER_NOTE = (
    "The 70 Subwoofer Crown WAVs live in the Free 808 Producer Kit repo on GitHub"
    " — there is no separate Subwoofer Crown repo."
)

SECTION_HEADERS = {
    "tizwildin_packs": '<section id="tizwildin-packs" class="wrap section"><h2>TizWildin sample packs</h2><p class="muted">Original TizWildin loop and stem collections — synthwave, dark cinematic, and chime lanes.</p><div class="catalog">',
    "producer_kits": '<section id="producer-kits" class="wrap section"><h2>Free producer kits</h2><p class="muted">Single-instrument and single-purpose free kits — 808s, drums, risers, keys, and bass.</p><div class="catalog">',
}

PRE_TEMPLATE = '<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n  <title>Free Sample Packs — TizWildin Entertainment HUB</title>\n  <meta name="description" content="13 free sample packs and producer kits from TizWildin Entertainment: free 808 kit, free drum one-shots, risers, dark piano, violin synth, phonk toolkit, synthwave loops and chimes. Free and open-source on GitHub.">\n  <meta name="keywords" content="free sample packs, free 808 kit, free drum one-shots, free riser pack, free piano sample kit, free violin samples, phonk sample pack, synthwave loops, free loops, producer kits, TizWildin, GareBear99">\n  <meta name="author" content="Gary Doman, GareBear99, TizWildin Entertainment">\n  <link rel="canonical" href="https://garebear99.github.io/TizWildinEntertainmentHUB/packs.html">\n  <meta property="og:title" content="Free Sample Packs — TizWildin Entertainment HUB">\n  <meta property="og:description" content="13 free sample packs and producer kits: 808s, drum one-shots, risers, piano, violin, phonk, synthwave loops and chimes. Free and open-source on GitHub.">\n  <meta property="og:type" content="website">\n  <meta property="og:url" content="https://garebear99.github.io/TizWildinEntertainmentHUB/packs.html">\n  <meta property="og:image" content="https://garebear99.github.io/TizWildinEntertainmentHUB/assets/social/hub-card.svg">\n  <meta name="twitter:card" content="summary_large_image">\n  <meta name="twitter:title" content="Free Sample Packs — TizWildin Entertainment HUB">\n  <meta name="twitter:description" content="13 free sample packs and producer kits from TizWildin Entertainment. Free and open-source on GitHub.">\n  <meta name="theme-color" content="#7c8cff">\n  <link rel="icon" href="assets/branding/favicon.svg" type="image/svg+xml">\n  <link rel="manifest" href="site.webmanifest">\n  <style>\n    :root{--bg:#050612;--panel:#0f1326;--panel2:#151b35;--line:#29345b;--text:#f8fbff;--muted:#aab4da;--accent:#7c8cff;--green:#35f0a3;--pink:#ff5ee7;--orange:#ff8b3d;--cyan:#56e6ff;--shadow:0 24px 90px rgba(0,0,0,.42)}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(circle at 9% 3%,rgba(124,140,255,.36),transparent 29%),radial-gradient(circle at 88% 16%,rgba(255,94,231,.22),transparent 27%),radial-gradient(circle at 45% 80%,rgba(53,240,163,.12),transparent 28%),linear-gradient(180deg,#050612,#0a1022 45%,#050612);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;line-height:1.55}a{color:inherit}.wrap{max-width:1220px;margin:0 auto;padding:0 22px}.nav{position:sticky;top:0;z-index:20;background:rgba(5,6,18,.78);backdrop-filter:blur(16px);border-bottom:1px solid rgba(255,255,255,.08)}.navin{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 0}.brand{display:flex;align-items:center;gap:10px;font-weight:950;letter-spacing:.2px;text-decoration:none}.brandmark{width:36px;height:36px;border-radius:13px;background:conic-gradient(from 210deg,var(--green),var(--cyan),var(--accent),var(--pink),var(--orange),var(--green));box-shadow:0 0 42px rgba(124,140,255,.6)}.links{display:flex;gap:14px;flex-wrap:wrap}.links a{color:var(--muted);font-size:13px;text-decoration:none;font-weight:750}.links a:hover{color:var(--text)}.hero{padding:78px 0 48px;position:relative}.eyebrow{display:inline-flex;gap:8px;align-items:center;border:1px solid rgba(124,140,255,.42);background:rgba(124,140,255,.14);color:#e6ebff;border-radius:999px;padding:8px 13px;font-size:13px;font-weight:850}.hero h1{font-size:clamp(43px,8.7vw,92px);line:.92;margin:22px 0 18px;letter-spacing:-3.5px;max-width:1050px}.grad{background:linear-gradient(90deg,var(--green),var(--cyan),var(--accent),var(--pink),var(--orange),var(--green));background-size:220% auto;-webkit-background-clip:text;background-clip:text;color:transparent;animation:gradShift 7s linear infinite}@keyframes gradShift{to{background-position:220% center}}@keyframes neonPulse{0%,100%{box-shadow:0 0 18px rgba(53,240,163,.35),0 0 42px rgba(124,140,255,.22)}50%{box-shadow:0 0 30px rgba(255,94,231,.45),0 0 64px rgba(124,140,255,.35)}}@keyframes liveBlink{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(53,240,163,.7)}50%{opacity:.55;box-shadow:0 0 0 7px rgba(53,240,163,0)}}.livedot{display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--green);margin-right:2px;animation:liveBlink 1.6s ease-in-out infinite}.eyebrow{animation:neonPulse 3.2s ease-in-out infinite}.section h2{text-shadow:0 0 24px rgba(124,140,255,.45)}.catalog .item{transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease}.catalog .item:hover{transform:translateY(-4px);border-color:rgba(124,140,255,.65);box-shadow:0 0 0 1px rgba(124,140,255,.35),0 0 34px rgba(124,140,255,.35),0 18px 50px rgba(0,0,0,.5)}.packlinks a:hover{color:#fff;text-shadow:0 0 12px rgba(86,230,255,.9)}.itch-row{display:flex;gap:12px;overflow-x:auto;padding:6px 2px 16px;scroll-snap-type:x mandatory;scrollbar-color:var(--accent) rgba(255,255,255,.07)}.itch-row::-webkit-scrollbar{height:10px}.itch-row::-webkit-scrollbar-thumb{background:linear-gradient(90deg,var(--green),var(--accent),var(--pink));border-radius:999px}.itch-row::-webkit-scrollbar-track{background:rgba(255,255,255,.07);border-radius:999px}.itch-chip{flex:0 0 248px;scroll-snap-align:start;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:16px;padding:13px 14px;text-decoration:none;display:flex;flex-direction:column;gap:5px;transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease}.itch-chip:hover{transform:translateY(-3px);border-color:rgba(255,94,231,.7);box-shadow:0 0 24px rgba(255,94,231,.35)}.itch-chip b{font-size:14px;line-height:1.35}.itch-rank{font-size:11px;font-weight:900;letter-spacing:.08em;color:var(--cyan)}.itch-price{font-size:12px;font-weight:900;color:var(--green)}.itch-price.paid{color:var(--orange)}.lead{font-size:clamp(17px,2.3vw,24px);color:var(--muted);max-width:920px}.cta{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}.btn{display:inline-flex;align-items:center;gap:9px;padding:13px 18px;border-radius:15px;border:1px solid rgba(255,255,255,.13);background:rgba(255,255,255,.07);text-decoration:none;font-weight:900;box-shadow:var(--shadow);transition:.18s transform,.18s border-color}.btn:hover{transform:translateY(-2px);border-color:rgba(255,255,255,.35)}.btn.primary{background:linear-gradient(135deg,var(--accent),#5668f2);color:white}.btn.green{background:linear-gradient(135deg,#1fa46d,var(--green));color:#06100b}.btn.orange{background:linear-gradient(135deg,#ff693d,var(--orange));color:#190801}.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:18px}.card{grid-column:span 4;background:linear-gradient(180deg,rgba(21,27,53,.9),rgba(10,14,28,.9));border:1px solid rgba(255,255,255,.1);border-radius:26px;padding:23px;box-shadow:var(--shadow)}.card h3{margin:0 0 8px;font-size:21px}.card p{margin:0;color:var(--muted)}.stat{font-size:38px;font-weight:1000;letter-spacing:-1px}.section{padding:46px 0}.section h2{font-size:clamp(29px,4vw,47px);margin:0 0 12px;letter-spacing:-1.7px}.muted{color:var(--muted)}.rail{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}.item{background:rgba(255,255,255,.058);border:1px solid rgba(255,255,255,.09);border-radius:19px;padding:17px;text-decoration:none}.item b{display:block;font-size:18px}.tag{display:inline-block;margin:8px 6px 0 0;padding:4px 8px;border-radius:999px;background:rgba(124,140,255,.16);color:#dce2ff;font-size:12px}.tag.green{background:rgba(53,240,163,.15);color:#caffea}.tag.orange{background:rgba(255,139,61,.16);color:#ffe0ca}.footer{border-top:1px solid rgba(255,255,255,.08);padding:32px 0;color:var(--muted);font-size:14px}.catalog{display:grid;grid-template-columns:repeat(auto-fit,minmax(285px,1fr));gap:14px}.catalog .item{min-height:190px;display:flex;flex-direction:column}.catalog .item p{flex:1}.packlinks{margin-top:12px;display:flex;gap:12px;flex-wrap:wrap;font-weight:800;font-size:14px}.packlinks a{color:#dce2ff}.note{background:linear-gradient(90deg,rgba(53,240,163,.12),rgba(124,140,255,.1));border:1px solid rgba(53,240,163,.25);border-radius:20px;padding:16px;color:#daf8ee}.crumbs{font-size:13px;color:var(--muted);margin:26px 0 0}.crumbs a{color:var(--muted)}@media(max-width:860px){.card{grid-column:span 12}.links{display:none}.hero h1{letter-spacing:-1.5px}}\n  </style>\n  <script type="application/ld+json">@@JSON_LD@@</script>\n</head>\n<body>\n<header class="nav"><div class="wrap navin"><a class="brand" href="index.html"><span class="brandmark"></span><span>TizWildin HUB</span></a><nav class="links"><a href="index.html">Dashboard</a><a href="index-seo.html">SEO Landing Page</a><a href="packs.html">Packs</a><a href="index.html#packs">Packs Tab</a><a href="ecosystem-index.html">Ecosystem Index</a><a href="https://github.com/GareBear99/TizWildinEntertainmentHUB">GitHub</a></nav></div></header>\n<main id="top">\n<p class="wrap crumbs"><a href="index.html">HUB dashboard</a> / <a href="index-seo.html">SEO landing page</a> / Free Sample Packs</p>\n<section class="hero wrap"><span class="eyebrow"><span class="livedot"></span>LIVE · 🎁 @@TOTAL@@ free packs · open-source on GitHub · free to use</span><h1>Free <span class="grad">Sample Packs</span> for producers.</h1><p class="lead">Every free TizWildin sample pack and producer kit in one crawlable place: synthwave loops, dark cinematic stems, chimes, 808s, drum one-shots, risers, piano, violin, phonk, and future bass. No paywall, no sign-up — download the samples free from GitHub.</p><div class="cta"><a class="btn primary" href="index.html#packs">🎁 Open the Packs Tab on the Dashboard</a><a class="btn green" href="https://github.com/GareBear99/awesome-audio-plugins-dev">🚀 Start Here List</a><a class="btn" href="ecosystem-index.html">🗂 Full Ecosystem Index</a></div></section>\n<section class="wrap section"><div class="grid"><article class="card"><div class="stat">@@TOTAL@@</div><h3>Free sample packs</h3><p>@@N_TIZ@@ TizWildin packs + @@N_KITS@@ free producer kits, all open-source on GitHub.</p></article><article class="card"><div class="stat">@@N_TIZ@@</div><h3>TizWildin packs</h3><p>Original Aurora, Obsidian, Skyline, Chroma, and Chime loop and stem collections.</p></article><article class="card"><div class="stat">@@N_KITS@@</div><h3>Free producer kits</h3><p>808s, drums, risers, piano, violin, phonk, future bass, and subwoofer bass.</p></article></div></section>\n\n'
TAIL_TEMPLATE = '<section class="wrap section"><div class="note"><b>Free GitHub packs vs. the itch store:</b><br>These 13 packs are free and open-source on GitHub. The GareBearProductionz itch store is a separate, mostly-paid catalog — a few packs overlap (Subwoofer Crown, the 808 kit, and the violin kit are also listed on itch, linked above). The itch row above lists all 112 store items in inventory order; the full inventory with covers lives on the <a href="pages/all-account-inventory.html">All Itch inventory page</a>.</div></section>\n\n<section class="wrap section"><h2>Where to go next</h2><div class="rail"><a class="item" href="index.html#packs"><b>🎛️ HUB Dashboard — Packs Tab</b><span class="small">The interactive 9-tab dashboard. The Packs tab renders these same 13 packs with live release checks.</span></a><a class="item" href="index-seo.html#packs"><b>🔎 General SEO Landing Page</b><span class="small">The HUB-wide SEO front door: plugins, packs, lists, routing, and proof in one page.</span></a><a class="item" href="https://github.com/GareBear99/awesome-audio-plugins-dev"><b>🚀 Start Here List</b><span class="small">The main public entry list for the GareBear99 / TizWildin audio ecosystem.</span></a><a class="item" href="pages/all-account-inventory.html"><b>🛒 All Itch Inventory</b><span class="small">The full GareBearProductionz itch catalog, including the paid versions of overlapping packs.</span></a><a class="item" href="ecosystem-index.html"><b>🗂 Public Ecosystem Index</b><span class="small">The static crawlable index of every plugin, pack, list, and ARC route.</span></a><a class="item" href="public-index.json"><b>{ } JSON Link Index</b><span class="small">Machine-readable public index (public-index.json) with all 13 pack routes.</span></a></div></section>\n</main><footer class="footer"><div class="wrap">Built by Gary Doman / GareBear99 / TizWildin Entertainment. Public rule: strong SEO, honest status, no fake production claims. All 13 packs above are free — no checkout on this page. Itch links in the row below go to the official itch listings.</div></footer>\n<p style="text-align:center;margin:32px"><a href="index.html">HUB Dashboard</a> · <a href="index-seo.html">SEO Landing Page</a> · <a href="ecosystem-index.html">Public Ecosystem Index</a> · <a href="public-index.json">JSON Link Index</a> · <a href="llms.txt">LLM Index</a> · <a href="sitemap.xml">Sitemap</a></p>\n</body></html>\n'


def slug(name):
    """Pack name -> pages/<slug>.html, as the hand-written page did."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def display_tags(pack):
    return DISPLAY_TAGS.get(pack["id"], list(pack["tags"]))


def render_card(pack):
    desc = DISPLAY_DESCRIPTION.get(pack["id"], pack["description"])
    tags = display_tags(pack)
    featured = bool(pack.get("featured"))
    cls = "item featured" if featured else "item"
    tag_html = "".join(
        f'<span class="tag orange">{html.escape(t, quote=False)}</span>' for t in tags
    )
    if featured:
        tag_html = '<span class="tag green">⭐ Featured</span>' + tag_html
    note = ""
    if pack["id"] == "subwoofer_crown_bass":
        note = f'<p class="muted" style="font-size:13px">{SUBWOOFER_NOTE}</p>'
    links = (
        f'<a href="pages/{slug(pack["name"])}.html">Pack page →</a>'
        f'<a href="{GITHUB}/{pack["repo"]}" target="_blank" rel="noopener">GitHub repo →</a>'
    )
    if pack["id"] in ITCH_LINKS:
        links += (
            f'<a href="{ITCH_LINKS[pack["id"]]}" target="_blank" rel="noopener">'
            "Also on itch →</a>"
        )
    return (
        f'<article class="{cls}"><b>🎁 {html.escape(pack["name"], quote=False)}</b>'
        f'<p class="muted">{html.escape(desc, quote=False)}</p>{note}<div>{tag_html}</div>'
        f'<div class="packlinks">{links}</div></article>'
    )


def build_json_ld(packs):
    parts = []
    for pack in packs:
        parts.append({
            "@type": "CreativeWork",
            "name": pack["name"],
            "description": pack["description"],
            "url": f"{BASE}/pages/{slug(pack['name'])}.html",
            "codeRepository": f"{GITHUB}/{pack['repo']}",
            "keywords": ", ".join(display_tags(pack) + ["sample-pack", "producer-tools"]),
        })
    doc = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Free Sample Packs — TizWildin Entertainment HUB",
        "description": "13 free sample packs and producer kits from TizWildin Entertainment: free 808 kit, free drum one-shots, risers, dark piano, violin synth, phonk toolkit, synthwave loops and chimes. Free and open-source on GitHub.",
        "url": f"{BASE}/packs.html",
        "isPartOf": {
            "@type": "WebSite",
            "name": "TizWildin Entertainment HUB",
            "url": f"{BASE}/",
        },
        "creator": {"@type": "Person", "name": "Gary Doman", "alternateName": "GareBear99"},
        "hasPart": parts,
    }
    return json.dumps(doc, ensure_ascii=False, separators=(",", ":"))


def extract_itch_section(text):
    """Verbatim itch-row section from the existing page (dated snapshot)."""
    start = text.index('<section id="itch-row"')
    end = text.index("</section>", start) + len("</section>")
    return text[start:end]


def generate():
    data = json.loads(PACKS_JSON.read_text(encoding="utf-8"))
    packs = data["packs"]
    categories = [c["id"] for c in data["categories"]]
    if not PACKS_HTML.exists():
        raise SystemExit(
            "packs.html not found: the generator preserves its itch-row "
            "section verbatim and will not invent one. Restore packs.html first."
        )
    itch = extract_itch_section(PACKS_HTML.read_text(encoding="utf-8"))

    total = len(packs)
    counts = {cid: sum(1 for p in packs if p["category"] == cid) for cid in categories}
    out = (
        PRE_TEMPLATE.replace("@@JSON_LD@@", build_json_ld(packs))
        .replace("@@TOTAL@@", str(total))
        .replace("@@N_TIZ@@", str(counts.get("tizwildin_packs", 0)))
        .replace("@@N_KITS@@", str(counts.get("producer_kits", 0)))
    )
    sections = []
    for cid in categories:
        members = [p for p in packs if p["category"] == cid]
        sections.append(
            SECTION_HEADERS[cid]
            + "\n"
            + "\n".join(render_card(p) for p in members)
            + "\n</div></section>"
        )
    out += "\n\n".join(sections)
    out += "\n\n" + itch + "\n\n" + TAIL_TEMPLATE
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate packs.html from packs.json.")
    ap.add_argument("--check", action="store_true",
                    help="compare generated output with packs.html instead of writing")
    args = ap.parse_args(argv)
    out = generate()
    if args.check:
        current = PACKS_HTML.read_text(encoding="utf-8")
        if out == current:
            print("packs.html is in sync with packs.json")
            return 0
        sys.stdout.writelines(difflib.unified_diff(
            current.splitlines(keepends=True), out.splitlines(keepends=True),
            fromfile="packs.html (current)", tofile="packs.html (generated)"))
        return 1
    PACKS_HTML.write_text(out, encoding="utf-8")
    DOCS_HTML.write_text(out, encoding="utf-8")
    print(f"Wrote {PACKS_HTML} and {DOCS_HTML} ({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
