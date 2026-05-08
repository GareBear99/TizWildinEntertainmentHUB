#!/usr/bin/env python3
"""Build the public SEO/indexing layer for TizWildinEntertainmentHUB.

The generator intentionally emits plain static files so GitHub Pages, search crawlers,
LLM crawlers, directory crawlers, and humans can inspect the ecosystem without running JS.
"""
from __future__ import annotations

import html
import json
import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAGES = DOCS / "pages"
ASSETS = DOCS / "assets"
SOCIAL = ASSETS / "social"
OWNER = "GareBear99"
BASE = "https://garebear99.github.io/TizWildinEntertainmentHUB"
GH = f"https://github.com/{OWNER}"
TODAY = date.today().isoformat()


def read_json(rel: str) -> dict:
    path = ROOT / rel
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def slug(s: str) -> str:
    s = s.replace("+", " plus ").replace("&", " and ")
    out = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return out or "item"


def trim(s: str, n: int = 155) -> str:
    s = " ".join((s or "").split())
    if len(s) <= n:
        return s
    return s[: n - 1].rsplit(" ", 1)[0] + "…"


@dataclass
class LinkItem:
    cluster: str
    kind: str
    name: str
    description: str
    repo: str = ""
    url: str = ""
    docs: str = ""
    status: str = ""
    tags: list[str] | None = None
    priority: int = 99
    license: str = ""
    language: str = ""
    source_manifest: str = ""

    @property
    def id(self) -> str:
        return slug(self.name)

    @property
    def page(self) -> str:
        return f"pages/{self.id}.html"

    @property
    def page_url(self) -> str:
        return f"{BASE}/{self.page}"

    @property
    def canonical_url(self) -> str:
        return self.url or (f"{GH}/{self.repo}" if self.repo else BASE)

    @property
    def repo_url(self) -> str:
        return f"{GH}/{self.repo}" if self.repo else ""

    @property
    def docs_url(self) -> str:
        return self.docs or (f"{self.repo_url}#readme" if self.repo_url else self.canonical_url)

    @property
    def github_topics_url(self) -> str:
        return f"https://github.com/topics/{quote(slug((self.tags or [self.kind])[0]))}"


def plugin_license(raw: dict) -> str:
    if raw.get("license"):
        return str(raw["license"])
    return "Free / open-source route"


def collect_items() -> list[LinkItem]:
    items: list[LinkItem] = []
    plugins = read_json("plugins.json")
    packs = read_json("packs.json")
    lists = read_json("lists.json")

    flagship = {"freeeq8", "therum", "xylocore"}
    for p in plugins.get("plugins", []):
        pid = p.get("id", "")
        tags = [str(x) for x in p.get("formats", [])] + [p.get("category", "audio-plugin"), "audio-plugin", "music-production"]
        items.append(LinkItem(
            cluster="TizWildin Audio Plugins",
            kind="Audio Plugin / Producer Tool",
            name=p["name"],
            description=p.get("description", ""),
            repo=p.get("repo", ""),
            status=p.get("status", "public route"),
            tags=[t for t in tags if t],
            priority=10 if pid in flagship else 30,
            license=plugin_license(p),
            language="C++ / JUCE" if any(x in p.get("description", "").lower() for x in ["juce", "vst", "plugin"]) else "Mixed",
            source_manifest="plugins.json",
        ))

    for p in packs.get("packs", []):
        items.append(LinkItem(
            cluster="TizWildin Sample Packs",
            kind="Sample Pack / Producer Resource",
            name=p["name"],
            description=p.get("description", ""),
            repo=p.get("repo", ""),
            status="free pack route",
            tags=[str(x) for x in p.get("tags", [])] + ["sample-pack", "producer-tools"],
            priority=40,
            license="Royalty-free / see repository",
            language="Audio assets / Markdown",
            source_manifest="packs.json",
        ))

    for item in lists.get("lists", []):
        items.append(LinkItem(
            cluster="Discovery Lists and Public Routes",
            kind=item.get("type", "Public List / Discovery Route"),
            name=item["name"],
            description=item.get("description", ""),
            repo=item.get("repo", ""),
            url=item.get("url", ""),
            status=item.get("status", "canonical route"),
            tags=[str(x) for x in item.get("tags", [])] + ["discovery", "seo"],
            priority=int(item.get("priority", 50)),
            license="See repository",
            language="Markdown / HTML" if item.get("repo") else "Web",
            source_manifest="lists.json",
        ))

    fixed = [
        ("Branching Strategy Route", "Repository Governance Route", "Public branch governance route for the TizWildin / ARC public-index operating system: main, develop, seo, submission, route, arc, audio, release, and hotfix branches with validation gates.", "TizWildinEntertainmentHUB", ["branching", "git", "release-management", "seo", "governance"], 2, "Markdown"),
        ("SEO Public Index Branch", "SEO Branch Route", "Branch route for sitemap, public-index JSON, route pages, schema metadata, OpenGraph cards, Twitter cards, social previews, llms.txt, and public link graph generation.", "TizWildinEntertainmentHUB", ["seo", "sitemap", "structured-data", "public-index", "github-pages"], 3, "Markdown"),
        ("LibHunt Submission Branch", "Submission Branch Route", "Branch route for completing LibHunt project details, alternatives, evidence notes, status tracking, and cross-linking across ARC and TizWildin ecosystem projects.", "public-credibility-seo-tracker", ["libhunt", "submission", "alternatives", "project-discovery"], 4, "Markdown"),
        ("ARC Source-Spine Branch", "ARC Branch Route", "Branch route for ARC-Neuron, ARC-Core, Lucifer Runtime, arc-language-module, Arc-RAR, OmniBinary, local AI lists, LLM lists, governance routes, and source-spine indexing.", "TizWildinEntertainmentHUB", ["arc", "local-ai", "llm", "source-spine", "ai-governance"], 5, "Markdown"),
        ("TizWildin Audio Cluster Branch", "Audio Branch Route", "Branch route for FreeEQ8, FreeVox8, TizWildinEntertainmentHUB, awesome-audio-plugins-dev, sample packs, audio directories, plugin lists, and creator-tool indexing.", "TizWildinEntertainmentHUB", ["audio-plugin", "juce", "dsp", "sample-packs", "music-production"], 6, "Markdown"),
        ("Release Candidate Branch", "Release Governance Route", "Branch route for freezing validated public-index builds after JSON, sitemap, route-page, branch-map, social-card, and release-readiness checks pass.", "TizWildinEntertainmentHUB", ["release", "validation", "ci", "public-index", "github-actions"], 7, "Markdown"),
        ("Public Credibility SEO Tracker", "Submission / Credibility Ledger", "Public credibility, SEO, and directory-submission tracker for the GareBear99 / TizWildin / ARC open-source ecosystem. Tracks LibHunt, GitHub Topics, Open Hub, SourceForge, awesome lists, audio directories, AI directories, and evidence notes.", "public-credibility-seo-tracker", ["seo", "submission-tracker", "credibility", "libhunt"], 8, "Markdown"),
        ("LibHunt Submission Route", "Directory Submission Route", "First public SEO and credibility submission platform for ARC and TizWildin project pages, alternatives, topic metadata, and public comparison graphs.", "public-credibility-seo-tracker", ["libhunt", "project-discovery", "alternatives", "seo"], 11, "Markdown"),
        ("GitHub Topics Cleanup Route", "Native GitHub SEO Route", "GitHub repository topic optimization route for local-ai, offline-ai, audio-plugin, juce, dsp, sample-pack, open-source-audio, and project discovery tags.", "public-credibility-seo-tracker", ["github-topics", "seo", "repo-discovery", "metadata"], 12, "Markdown"),
        ("Open Hub Submission Route", "Open Source Index Route", "Open Hub / Black Duck project indexing route for open-source credibility, activity metadata, repository history, and public project discovery.", "public-credibility-seo-tracker", ["openhub", "open-source", "credibility", "project-index"], 13, "Markdown"),
        ("SourceForge Mirror Route", "Release Mirror Route", "SourceForge project mirror and release route for plugin/tool downloads, project pages, release metadata, and externally indexed distribution surfaces.", "public-credibility-seo-tracker", ["sourceforge", "downloads", "release-mirror", "open-source"], 14, "Markdown"),
        ("Awesome Lists Submission Route", "Curated List Submission Route", "GitHub PR-based submission route for awesome-local-llm, awesome-local-ai, awesome-ai-agents, awesome-juce, audio DSP lists, and music-production discovery lists.", "public-credibility-seo-tracker", ["awesome-lists", "curated-lists", "pull-request", "seo"], 15, "Markdown"),
        ("OpenAlternative Submission Route", "Open Source Alternative Route", "OpenAlternative and OpenSourceAlternative.to submission route for positioning ARC and TizWildin projects as open-source alternatives to paid, cloud, or closed creator and AI tools.", "public-credibility-seo-tracker", ["openalternative", "open-source-alternative", "directory", "seo"], 16, "Markdown"),
        ("Audio Directory Submission Route", "Audio Plugin Directory Route", "Audio directory route for KVR Audio, Audio Plugins for Free, Bedroom Producers Blog, OpenAudio, JUCE lists, and producer-facing plugin discovery surfaces.", "public-credibility-seo-tracker", ["audio-directory", "vst3", "juce", "music-production"], 17, "Markdown"),
        ("ARC-Neuron-LLMBuilder", "ARC Local AI / LLM Builder", "Local-first cognition-core builder for dataset preparation, model-building experiments, GGUF-oriented local AI workflows, receipts, and reproducible AI growth pipelines.", "ARC-Neuron-LLMBuilder", ["local-ai", "llm", "gguf", "cognition-core"], 5, "Python"),
        ("ARC-Core", "ARC Authority Spine", "Signal-intelligence event spine and local-first AI governance console for deterministic routing, authority gates, receipts, calibration, incident tracking, and replayable evidence.", "ARC-Core", ["arc", "ai-governance", "receipts", "event-sourcing"], 6, "Python"),
        ("arc-lucifer-cleanroom-runtime", "ARC Cleanroom Runtime", "Local-first cleanroom AI runtime route for offline model execution, token streaming, deterministic event capture, and reproducible inference behavior.", "arc-lucifer-cleanroom-runtime", ["local-ai", "runtime", "offline-ai", "llamafile"], 7, "Python"),
        ("arc-language-module", "ARC Language Module", "Language and cognition foundation route for linguistic structure, transliteration, lineage, phonology, and language-learning data.", "arc-language-module", ["nlp", "linguistics", "language-learning"], 8, "Python"),
        ("Arc-RAR", "ARC Archive Manager", "CLI-first archive manager with native-app control plane, autowrap intent validation, receipts, restore paths, and reproducible project archive handling.", "Arc-RAR", ["archive", "reproducibility", "cli", "receipts"], 9, "Rust"),
        ("OmniBinary Runtime", "Binary Intake / Runtime Scaffold", "Native-first binary intake and execution-fabric scaffold for file inspection, host profiling, lane selection, receipts, audits, and runtime-readiness reporting.", "omnibinary-runtime", ["binary-runtime", "receipts", "native-first"], 10, "Rust"),
        ("Ecosystem Search", "Public Search Route", "Static full-text search route across public project pages, source repository files, extracted links, route metadata, and submission/discovery records.", "TizWildinEntertainmentHUB", ["search", "source-index", "link-graph", "seo", "public-index"], 1, "HTML / JSON"),
        ("Public Index Health Dashboard", "Index Health Route", "Public health dashboard for route counts, sitemap coverage, source repository indexing, extracted links, full-text search records, readiness scores, and benchmark grade.", "TizWildinEntertainmentHUB", ["index-health", "benchmark", "validation", "quality", "seo"], 1, "HTML / JSON"),
        ("Repository Readiness Report", "Repository Quality Route", "Scored readiness report for indexed repositories covering README, license, changelog, contributing guide, security policy, CI, docs, links, and source coverage.", "TizWildinEntertainmentHUB", ["readiness", "repository-quality", "submission-readiness", "seo", "open-source"], 1, "HTML / JSON"),
        ("Ecosystem File Search", "Source File Search Route", "Queryable source-repository file and link lookup page for indexed ARC and TizWildin repositories.", "TizWildinEntertainmentHUB", ["file-search", "source-index", "repo-search", "link-search"], 1, "HTML / JSON"),
    ]
    existing = {i.name.lower() for i in items}
    for name, kind, desc, repo, tags, prio, lang in fixed:
        if name.lower() in existing:
            continue
        items.append(LinkItem(
            cluster="ARC Source Spine" if name != "Public Credibility SEO Tracker" else "Credibility and Submission Tracking",
            kind=kind,
            name=name,
            description=desc,
            repo=repo,
            status="public route",
            tags=tags,
            priority=prio,
            license="MIT / see repository",
            language=lang,
            source_manifest="generator fixed routes",
        ))

    # Deduplicate by page id, keeping the highest-priority item.
    dedup: dict[str, LinkItem] = {}
    for item in sorted(items, key=lambda x: (x.priority, x.name.lower())):
        dedup.setdefault(item.id, item)
    return sorted(dedup.values(), key=lambda x: (x.cluster, x.priority, x.name.lower()))


def social_card(title: str, subtitle: str, filename: str) -> str:
    title = html.escape(trim(title, 60))
    subtitle = html.escape(trim(subtitle, 120))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <radialGradient id="g" cx="35%" cy="20%" r="90%"><stop stop-color="#263676"/><stop offset="0.45" stop-color="#080a16"/><stop offset="1" stop-color="#050611"/></radialGradient>
    <linearGradient id="line" x1="0" x2="1"><stop stop-color="#8ea2ff"/><stop offset="1" stop-color="#69f0ae"/></linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#g)"/>
  <circle cx="1030" cy="110" r="220" fill="#8ea2ff" opacity="0.14"/>
  <circle cx="130" cy="540" r="260" fill="#69f0ae" opacity="0.10"/>
  <rect x="70" y="70" width="1060" height="490" rx="34" fill="#10162d" opacity="0.88" stroke="#35416e"/>
  <rect x="70" y="70" width="1060" height="8" fill="url(#line)"/>
  <text x="100" y="150" fill="#86efac" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="700" letter-spacing="4">TIZWILDIN ENTERTAINMENT HUB</text>
  <text x="100" y="295" fill="#f3f6ff" font-family="Arial, Helvetica, sans-serif" font-size="68" font-weight="800">{title}</text>
  <foreignObject x="100" y="330" width="980" height="145"><div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Arial,Helvetica,sans-serif;color:#b9c3e8;font-size:30px;line-height:1.3">{subtitle}</div></foreignObject>
  <text x="100" y="515" fill="#8ea2ff" font-family="Arial, Helvetica, sans-serif" font-size="27" font-weight="700">garebear99.github.io/TizWildinEntertainmentHUB</text>
</svg>'''
    write(SOCIAL / filename, svg)
    return f"{BASE}/assets/social/{filename}"


def base_head(title: str, description: str, canonical: str, jsonld: dict | list | None = None, image: str | None = None) -> str:
    image = image or f"{BASE}/assets/social/hub-card.svg"
    ld = ""
    if jsonld:
        ld = '<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False, indent=2) + "</script>"
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(trim(description, 158))}">
<link rel="canonical" href="{html.escape(canonical)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="author" content="GareBear99 / TizWildin Entertainment">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(trim(description, 200))}">
<meta property="og:type" content="website">
<meta property="og:url" content="{html.escape(canonical)}">
<meta property="og:image" content="{html.escape(image)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(trim(description, 200))}">
<meta name="twitter:image" content="{html.escape(image)}">
{ld}'''


def css() -> str:
    return '''<style>
:root{--bg:#070914;--card:#11152a;--line:#28304f;--text:#f3f6ff;--muted:#aab3cf;--accent:#8ea2ff;--green:#69f0ae;--gold:#f8d36f}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#151a35,#070914 46%);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;line-height:1.55}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}.wrap{max-width:1180px;margin:0 auto;padding:36px 20px 64px}.hero{border:1px solid var(--line);background:linear-gradient(135deg,rgba(142,162,255,.16),rgba(105,240,174,.07));border-radius:24px;padding:28px;margin-bottom:20px;box-shadow:0 18px 70px rgba(0,0,0,.25)}h1{margin:0 0 8px;font-size:clamp(30px,6vw,56px);letter-spacing:-.05em}h2{margin-top:34px}p{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}.card{border:1px solid var(--line);background:rgba(17,21,42,.92);border-radius:18px;padding:18px;min-height:188px;display:flex;flex-direction:column;gap:10px}.card h3{margin:0;font-size:20px}.badge{display:inline-block;width:max-content;border:1px solid rgba(105,240,174,.35);color:var(--green);border-radius:999px;padding:3px 9px;font-size:12px;text-transform:uppercase;letter-spacing:.08em}.links{display:flex;gap:8px;flex-wrap:wrap;margin-top:auto}.links a{border:1px solid var(--line);background:#172044;border-radius:10px;padding:8px 10px;font-weight:700}.tags{display:flex;gap:6px;flex-wrap:wrap}.tag{font-size:12px;color:#cbd3ff;background:#1a203b;border-radius:999px;padding:3px 8px}.nav{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}.nav a{border:1px solid var(--line);border-radius:12px;padding:9px 12px;background:#11152a;font-weight:700}.small{font-size:13px;color:var(--muted)}table{width:100%;border-collapse:collapse;background:#10152a;border:1px solid var(--line);border-radius:14px;overflow:hidden}th,td{border-bottom:1px solid var(--line);padding:10px;text-align:left;vertical-align:top}th{color:var(--green);font-size:13px;text-transform:uppercase;letter-spacing:.08em}code{background:#101936;border:1px solid var(--line);border-radius:7px;padding:2px 6px}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}.callout{border-left:4px solid var(--green);background:#101936;border-radius:14px;padding:14px 16px}.crumbs{font-size:13px;color:var(--muted);margin-bottom:14px}.score{color:var(--gold);font-weight:800}</style>'''


def html_page(title: str, description: str, body: str, canonical: str, jsonld: dict | list | None = None, image: str | None = None) -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
{base_head(title, description, canonical, jsonld, image)}
{css()}
</head>
<body><main class="wrap">{body}</main></body></html>
'''


def item_card(item: LinkItem) -> str:
    tags = "".join(f'<span class="tag">{html.escape(str(t))}</span>' for t in (item.tags or [])[:8] if t)
    return f'''<article class="card">
<span class="badge">{html.escape(item.kind)}</span>
<h3><a href="{html.escape(item.page)}">{html.escape(item.name)}</a></h3>
<p>{html.escape(item.description)}</p>
<div class="tags">{tags}</div>
<div class="links">
<a href="{html.escape(item.page)}">Index page</a>
<a href="{html.escape(item.canonical_url)}" rel="noopener">Public URL</a>
{f'<a href="{html.escape(item.repo_url)}" rel="noopener">GitHub</a>' if item.repo_url else ''}
</div>
</article>'''


def item_jsonld(item: LinkItem) -> dict:
    kind = "SoftwareSourceCode" if item.repo else "CreativeWork"
    if "Sample Pack" in item.kind:
        kind = "CreativeWork"
    return {
        "@context": "https://schema.org",
        "@type": kind,
        "name": item.name,
        "description": item.description,
        "url": item.page_url,
        "codeRepository": item.repo_url or None,
        "license": item.license or None,
        "programmingLanguage": item.language or None,
        "applicationCategory": item.kind,
        "creator": {"@type": "Person", "name": "Gary Doman / GareBear99"},
        "isPartOf": {"@type": "WebSite", "name": "TizWildin Entertainment HUB", "url": BASE},
        "sameAs": [x for x in [item.canonical_url, item.repo_url, item.docs_url] if x],
        "keywords": ", ".join(item.tags or []),
    }


def render_item_page(item: LinkItem, all_items: list[LinkItem]) -> None:
    related = [x for x in all_items if x.cluster == item.cluster and x.id != item.id][:8]
    related_links = "".join(f'<li><a href="{html.escape(x.page)}">{html.escape(x.name)}</a> — {html.escape(x.kind)}</li>' for x in related)
    tags = "".join(f'<span class="tag">{html.escape(str(t))}</span>' for t in (item.tags or []) if t)
    desc = f"{item.name} public route in the TizWildin / ARC ecosystem: {item.description}"
    image = social_card(item.name, item.description, f"{item.id}-card.svg")
    body = f'''<div class="crumbs"><a href="../ecosystem-index.html">Ecosystem index</a> / {html.escape(item.cluster)}</div>
<section class="hero"><span class="badge">{html.escape(item.kind)}</span><h1>{html.escape(item.name)}</h1><p>{html.escape(item.description)}</p>
<div class="nav"><a href="{html.escape(item.canonical_url)}">Open public URL</a>{f'<a href="{html.escape(item.repo_url)}">GitHub repository</a>' if item.repo_url else ''}<a href="{html.escape(item.docs_url)}">Docs / README</a><a href="../public-index.json">JSON index</a><a href="../sitemap.xml">Sitemap</a></div></section>
<section class="callout"><strong>Index purpose:</strong> This static page gives crawlers, directories, LLM readers, and humans a dedicated canonical route for this project instead of hiding it inside JavaScript UI state.</section>
<h2>Public metadata</h2><table><tbody>
<tr><th>Cluster</th><td>{html.escape(item.cluster)}</td></tr>
<tr><th>Status</th><td>{html.escape(item.status or 'public route')}</td></tr>
<tr><th>Repository</th><td>{f'<a href="{html.escape(item.repo_url)}">{html.escape(item.repo_url)}</a>' if item.repo_url else 'N/A'}</td></tr>
<tr><th>Docs</th><td><a href="{html.escape(item.docs_url)}">{html.escape(item.docs_url)}</a></td></tr>
<tr><th>Language</th><td>{html.escape(item.language or 'See repository')}</td></tr>
<tr><th>License</th><td>{html.escape(item.license or 'See repository')}</td></tr>
<tr><th>Source manifest</th><td><code>{html.escape(item.source_manifest)}</code></td></tr>
</tbody></table>
<h2>SEO tags</h2><div class="tags">{tags}</div>
<h2>Related ecosystem routes</h2><ul>{related_links or '<li>No same-cluster route detected.</li>'}</ul>
<p class="small">Generated {TODAY}. This page is part of the static public link graph for TizWildinEntertainmentHUB.</p>'''
    write(DOCS / item.page, html_page(f"{item.name} | TizWildin Ecosystem Index", desc, body, item.page_url, item_jsonld(item), image))


def build() -> None:
    DOCS.mkdir(exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)
    SOCIAL.mkdir(parents=True, exist_ok=True)
    items = collect_items()
    social_card("Public Ecosystem Index", "Free audio plugins, sample packs, ARC source-spine repos, awesome lists, and public credibility routes.", "hub-card.svg")

    # Per-item route pages.
    for item in items:
        render_item_page(item, items)

    public_index = {
        "schemaVersion": "2.0",
        "generatedAt": TODAY,
        "name": "TizWildin Entertainment HUB Public Link Index",
        "description": "Static crawler-friendly index of TizWildin audio, producer, public list, credibility, and ARC source-spine routes.",
        "owner": OWNER,
        "baseUrl": BASE,
        "itemCount": len(items),
        "items": [asdict(i) | {
            "id": i.id,
            "page": i.page,
            "pageUrl": i.page_url,
            "canonicalUrl": i.canonical_url,
            "repoUrl": i.repo_url,
            "docsUrl": i.docs_url,
        } for i in items],
    }
    write(DOCS / "public-index.json", json.dumps(public_index, indent=2, ensure_ascii=False))

    by_cluster: dict[str, list[LinkItem]] = {}
    for i in items:
        by_cluster.setdefault(i.cluster, []).append(i)

    body = '''<section class="hero"><h1>TizWildin Entertainment HUB</h1>
<p>GitHub-Pages-friendly public index for free audio plugins, sample packs, awesome lists, creator tools, public credibility submission routes, and the ARC source-spine routes connected to the GareBear99 ecosystem.</p>
<div class="nav"><a href="index.html">Interactive dashboard</a><a href="index-seo.html">SEO landing page</a><a href="arc-index.html">ARC source spine</a><a href="public-index.json">JSON index</a><a href="llms.txt">LLM text index</a><a href="PUBLIC_LINK_GRAPH.md">Link graph</a><a href="sitemap.xml">Sitemap</a></div></section>'''
    for cluster, vals in by_cluster.items():
        body += f'<h2>{html.escape(cluster)}</h2><section class="grid">' + ''.join(item_card(v) for v in vals) + '</section>'
    graph = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "TizWildin Entertainment HUB Public Ecosystem Index", "url": f"{BASE}/ecosystem-index.html", "description": public_index["description"], "hasPart": [{"@type": "WebPage", "name": i.name, "url": i.page_url} for i in items]}
    write(DOCS / "ecosystem-index.html", html_page("TizWildin Entertainment HUB Public Ecosystem Index", public_index["description"], body, f"{BASE}/ecosystem-index.html", graph))

    arc_items = [i for i in items if i.cluster in {"ARC Source Spine", "Credibility and Submission Tracking"}]
    arc_body = '''<section class="hero"><h1>ARC Source Spine</h1><p>Static public route map for the ARC local AI, runtime, archive, binary, and credibility-tracking repositories linked from the TizWildin ecosystem.</p><div class="nav"><a href="ecosystem-index.html">Full ecosystem</a><a href="public-index.json">JSON index</a><a href="llms.txt">LLM index</a></div></section><section class="grid">''' + ''.join(item_card(i) for i in arc_items) + '</section>'
    write(DOCS / "arc-index.html", html_page("ARC Source Spine | TizWildin HUB", "Local-first ARC repository map for ARC-Neuron, ARC-Core, Lucifer runtime, language module, Arc-RAR, OmniBinary, and public credibility routes.", arc_body, f"{BASE}/arc-index.html", {"@context":"https://schema.org","@type":"CollectionPage","name":"ARC Source Spine","url":f"{BASE}/arc-index.html"}))

    # A compact index intended for AI crawlers and code assistants.
    llms_lines = [
        "# TizWildin Entertainment HUB Public Index",
        "",
        f"Generated: {TODAY}",
        f"Base URL: {BASE}",
        "",
        "This is the crawler/LLM-friendly plain text index for the GareBear99 / TizWildin / ARC ecosystem.",
        "",
    ]
    for cluster, vals in by_cluster.items():
        llms_lines += [f"## {cluster}", ""]
        for i in vals:
            llms_lines += [f"- {i.name}: {i.description}", f"  Page: {i.page_url}", f"  Public URL: {i.canonical_url}", f"  GitHub: {i.repo_url or 'N/A'}", f"  Tags: {', '.join(i.tags or [])}", ""]
    write(DOCS / "llms.txt", "\n".join(llms_lines))

    # Markdown link graph / audit map.
    md = ["# Public Link Graph", "", f"Generated: {TODAY}", "", "This file documents every static route generated for the TizWildinEntertainmentHUB public ecosystem index.", "", "## Summary", "", f"- Total indexed records: **{len(items)}**", f"- Total clusters: **{len(by_cluster)}**", "- Generator: `scripts/build_public_index.py`", "- Validator: `scripts/validate_public_index.py`", "", "## Routes", ""]
    for cluster, vals in by_cluster.items():
        md += [f"### {cluster}", "", "| Route | Type | Repository | Tags |", "|---|---|---|---|"]
        for i in vals:
            md.append(f"| [{i.name}]({i.page}) | {i.kind} | {i.repo_url or i.canonical_url} | {', '.join(i.tags or [])} |")
        md.append("")
    write(DOCS / "PUBLIC_LINK_GRAPH.md", "\n".join(md))

    # Sitemap includes dashboard, indexes, route pages, and social cards.
    urls = ["", "index.html", "index-seo.html", "ecosystem-index.html", "arc-index.html", "public-index.json", "llms.txt", "PUBLIC_LINK_GRAPH.md"]
    urls += [i.page for i in items]
    urls += [f"assets/social/{p.name}" for p in SOCIAL.glob("*.svg")]
    seen = []
    for u in urls:
        loc = BASE + ("/" + u if u else "/")
        if loc not in seen:
            seen.append(loc)
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc in seen:
        sitemap.append(f"  <url><loc>{xml_escape(loc)}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>{'1.0' if loc.endswith('/') else '0.8'}</priority></url>")
    sitemap.append("</urlset>")
    write(DOCS / "sitemap.xml", "\n".join(sitemap))

    robots = f"""User-agent: *
Allow: /

Sitemap: {BASE}/sitemap.xml

# Public machine-readable indexes
Allow: /TizWildinEntertainmentHUB/public-index.json
Allow: /TizWildinEntertainmentHUB/llms.txt
"""
    write(DOCS / "robots.txt", robots)

    # Web manifest.
    manifest = {
        "name": "TizWildin Entertainment HUB",
        "short_name": "TizWildin HUB",
        "description": public_index["description"],
        "start_url": "/TizWildinEntertainmentHUB/",
        "display": "standalone",
        "background_color": "#070914",
        "theme_color": "#8ea2ff",
    }
    write(DOCS / "site.webmanifest", json.dumps(manifest, indent=2))

    # Validation manifest for CI.
    audit = {
        "generatedAt": TODAY,
        "items": len(items),
        "clusters": {k: len(v) for k, v in by_cluster.items()},
        "sitemapUrls": len(seen),
        "routePages": len(list(PAGES.glob("*.html"))),
        "socialCards": len(list(SOCIAL.glob("*.svg"))),
    }
    write(DOCS / "SEO_BUILD_REPORT.json", json.dumps(audit, indent=2))

    print(f"Built public index: {len(items)} records, {len(seen)} sitemap URLs, {audit['socialCards']} social cards")


if __name__ == "__main__":
    build()
