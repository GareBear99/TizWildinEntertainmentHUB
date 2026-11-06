#!/usr/bin/env python3
"""Real link checker for TizWildinEntertainmentHUB.

Replaces the old "offline-format" checker (which validated URL *syntax*
only: 740 links, 0 checked). This one actually checks links:

- Internal links: every href/src in every HTML file under docs/ (plus the
  root index.html / index-seo.html mirrors) is resolved against the local
  filesystem and verified to exist; fragment anchors (#id) are verified
  against id= attributes in the target page.
- External links: every distinct http(s) URL found in the crawled pages,
  in public-index.json, and in source-link-index.json is fetched live
  (HEAD, with a GET fallback for servers that reject HEAD). One retry on
  429/5xx after a short backoff. 429/403 responses are reported as
  "blocked" (rate-limited / bot-gated), NOT as broken — itch.io and GitHub
  throttle automated checks, and a throttle is not a dead link.
- Skipped, with reasons, not silently: template placeholders ({...}),
  example.local / example.com fixtures, mailto:/tel:/javascript: links,
  and the meta-records that source-link-index extracted from the old
  LINK_CHECK_REPORT.json itself (a report about links is not a link).

Writes docs/LINK_CHECK_REPORT.json (schema 1.0, same top-level fields as
before plus internal/external breakdowns) and exits 1 when live issues
were found, so CI can gate on it.

Usage:
    python3 scripts/check_public_links.py            # live check (default)
    CHECK_EXTERNAL_LINKS=0 python3 scripts/check_public_links.py
                                                       # offline: format + internal only
    LINK_CHECK_BASE_TIMEOUT=10 LINK_CHECK_MAX_LINKS=3000 \
    LINK_CHECK_WORKERS=10 python3 scripts/check_public_links.py
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FETCH = os.environ.get("CHECK_EXTERNAL_LINKS", "1") != "0"
TIMEOUT = float(os.environ.get("LINK_CHECK_BASE_TIMEOUT", "10"))
MAX = int(os.environ.get("LINK_CHECK_MAX_LINKS", "3000"))
WORKERS = int(os.environ.get("LINK_CHECK_WORKERS", "10"))
BASE = "https://garebear99.github.io/TizWildinEntertainmentHUB"
SITE_PREFIX = "/TizWildinEntertainmentHUB"

URL_RE = re.compile(r"^https?://[^\s<>\"']+$")
PLACEHOLDER_HOSTS = {"example.local", "example.com", "example.org", "example.net"}
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:", "blob:")
USER_AGENT = "TizWildinPublicIndexChecker/2.0 (+https://garebear99.github.io/TizWildinEntertainmentHUB/)"


def load(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


class LinkExtractor(HTMLParser):
    """Collects href/src attributes and id= anchors from one HTML file."""

    ATTRS = {
        ("a", "href"), ("link", "href"), ("img", "src"), ("script", "src"),
        ("iframe", "src"), ("source", "src"), ("embed", "src"),
        ("video", "src"), ("audio", "src"),
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.ids: set[str] = set()
        self._in_script = False
        self._script_buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if (tag, "href") in self.ATTRS and attrs.get("href"):
            self.links.append(attrs["href"])
        if (tag, "src") in self.ATTRS and attrs.get("src"):
            self.links.append(attrs["src"])
        if tag == "script":
            self._in_script = True
            self._script_buf = []

    def handle_endtag(self, tag):
        if tag == "script" and self._in_script:
            self._in_script = False
            text = "".join(self._script_buf)
            # Dashboard data sources live in inline JS (fetch / const URL =).
            # Only accept clean, complete http(s) literals — no templates,
            # no string-terminator characters (quote/backtick) in the match.
            for m in re.finditer(r"https?://[A-Za-z0-9\-._~:/?#@!$&()*+,;=%]+", text):
                url = m.group(0).rstrip(".,;)]}")
                if "{" not in url and "}" not in url and "$" not in url:
                    self.links.append(url)

    def handle_data(self, data):
        if self._in_script:
            self._script_buf.append(data)


def html_files() -> list[Path]:
    files = sorted(DOCS.rglob("*.html"))
    for name in ("index.html", "index-seo.html"):
        if (ROOT / name).exists():
            files.append(ROOT / name)
    return files


def parse_file(path: Path) -> tuple[list[str], set[str]]:
    try:
        parser = LinkExtractor()
        parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
        return parser.links, parser.ids
    except Exception as exc:  # unreadable file: report, don't crash the run
        return [], set()


def file_ids(path: Path, cache: dict[Path, set[str]]) -> set[str]:
    if path not in cache:
        _, ids = parse_file(path)
        cache[path] = ids
    return cache[path]


def is_loopback(url: str) -> bool:
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    return host in ("localhost", "127.0.0.1", "::1", "testserver") or host.endswith(".localhost") or host.endswith(".local")


def is_extraction_artifact(url: str) -> bool:
    """URLs that were never links: regex fragments, escaped dots, stray
    backticks/quotes, markdown bold markers left by a source indexer that
    scraped code text."""
    return ("\\" in url or "`" in url or "[^" in url or "**" in url
            or "example-repo" in url or url.rstrip("/").endswith("/repos"))


def check_external(url: str) -> tuple[str, int | None, str]:
    """Returns (status, http_code, error). 429/403 -> 'blocked', not broken."""
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    # Percent-encode non-ASCII (emoji badge URLs) — urllib cannot fetch raw UTF-8.
    safe = ":/?#@!$&'()*+,;=%-._~"
    url = urllib.parse.quote(url, safe=safe)
    # One retry on transport errors (itch.io and friends reset connections
    # under load from this egress IP; a single retry separates throttling
    # from genuinely dead links).
    for attempt in range(2):
        result = _fetch_once(url, headers)
        if result[0] != "fetch-error" or attempt == 1:
            return result
        time.sleep(2)
    return "fetch-error", None, "HEAD and GET both failed"


def _fetch_once(url: str, headers: dict) -> tuple[str, int | None, str]:
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return "ok", resp.status, ""
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 403):
                return "blocked", exc.code, f"HTTP {exc.code} (rate-limited/bot-gated, not counted as broken)"
            if exc.code in (404, 405, 501) and method == "HEAD":
                continue  # server answers GET only (edge workers, APIs); retry with GET
            if exc.code >= 400:
                # One retry for transient server errors.
                if exc.code >= 500:
                    time.sleep(2)
                    try:
                        req = urllib.request.Request(url, method="GET", headers=headers)
                        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                            return "ok", resp.status, ""
                    except Exception:
                        pass
                return "http-error", exc.code, f"HTTP {exc.code}"
            return "ok", exc.code, ""
        except Exception as exc:  # DNS, timeout, TLS, connection reset, ...
            return "fetch-error", None, str(exc)[:180]
    return "fetch-error", None, "HEAD and GET both failed"


def main() -> int:
    started = time.time()
    results: list[dict] = []
    seen: dict[str, dict] = {}  # url -> first-seen record (dedup for fetching)

    def add(url: str, source: str, item: str, kind: str) -> None:
        key = url
        if key not in seen:
            seen[key] = {"url": url, "source": source, "item": item, "kind": kind}
            results.append(seen[key])

    # --- 1. Crawl HTML pages (internal + external hrefs) -------------------
    id_cache: dict[Path, set[str]] = {}
    internal_issues = 0
    internal_checked = 0
    for path in html_files():
        rel = str(path.relative_to(ROOT))
        # Root index.html / index-seo.html are mirrors of the docs/ files:
        # their relative links resolve against docs/, where the site is served.
        resolve_base = DOCS if path.parent == ROOT else path.parent
        links, _ids = parse_file(path)
        # A bare origin used as a JS base constant (const ARC = 'https://…';
        # ARC + '/hub/community-stats') is not a link — the real endpoints
        # built from it are checked separately. Drop it when another link in
        # the same file extends it with a path.
        bare_bases = {u for u in links
                      if re.match(r"^https?://[^/]+/?$", (u or "").strip())}
        links = [u for u in links
                 if not (u in bare_bases
                         and any(v.startswith(u.rstrip("/") + "/") for v in links if v != u))]
        for raw in links:
            href = (raw or "").strip()
            if not href:
                continue
            if href.startswith(SKIP_SCHEMES):
                results.append({"url": href, "source": rel, "item": path.name,
                                "kind": "skipped-scheme", "status": "skipped",
                                "statusCode": None, "error": "non-http scheme"})
                continue
            if "{" in href or "}" in href or "${" in href:
                results.append({"url": href, "source": rel, "item": path.name,
                                "kind": "skipped-template", "status": "skipped",
                                "statusCode": None, "error": "template placeholder, not a real URL"})
                continue
            parsed = urllib.parse.urlparse(href)
            if parsed.scheme in ("http", "https") or href.startswith("//"):
                url = href if parsed.scheme else "https:" + href
                host = urllib.parse.urlparse(url).hostname or ""
                if host in PLACEHOLDER_HOSTS:
                    results.append({"url": url, "source": rel, "item": path.name,
                                    "kind": "skipped-placeholder", "status": "skipped",
                                    "statusCode": None, "error": "placeholder fixture host"})
                    continue
                if is_loopback(url) or is_extraction_artifact(url):
                    results.append({"url": url, "source": rel, "item": path.name,
                                    "kind": "skipped-artifact", "status": "skipped",
                                    "statusCode": None,
                                    "error": "loopback/dev host or extraction artifact, not a site link"})
                    continue
                # Same-site URLs are verified against this checkout, not the
                # live deployment (which lags the working tree by design).
                if url.startswith(BASE + "/"):
                    internal_checked += 1
                    local = urllib.parse.unquote(url[len(BASE) + 1:].split("#", 1)[0].split("?", 1)[0])
                    frag = url.partition("#")[2]
                    target = DOCS / local
                    if target.is_dir():
                        target = target / "index.html"
                    status, err = "ok", ""
                    if not target.exists():
                        status, err = "broken-internal", f"same-site target missing locally: {local}"
                        internal_issues += 1
                    elif frag and frag not in file_ids(target, id_cache):
                        status, err = "broken-anchor", f"#{frag} not found in {target.relative_to(ROOT)}"
                        internal_issues += 1
                    results.append({"url": url, "source": rel, "item": path.name,
                                    "kind": "internal", "status": status,
                                    "statusCode": None, "error": err})
                    continue
                add(url, rel, path.name, "external")
                continue
            # Internal link.
            internal_checked += 1
            nofrag, _, frag = href.partition("#")
            target: Path | None = None
            if nofrag == "":
                target = path  # same-page anchor
            else:
                clean = urllib.parse.unquote(nofrag.split("?", 1)[0])
                if clean.startswith(SITE_PREFIX + "/"):
                    target = DOCS / clean[len(SITE_PREFIX) + 1:]
                elif clean.startswith("/"):
                    target = DOCS / clean.lstrip("/")
                else:
                    target = (resolve_base / clean).resolve()
                    # Containment: never escape the repo.
                    try:
                        target.relative_to(ROOT.resolve())
                    except ValueError:
                        target = None
                if target is not None and target.is_dir():
                    target = target / "index.html"
            status, code, err = "ok", None, ""
            if target is None or not target.exists():
                status, err = "broken-internal", f"target does not exist: {nofrag or '(same page)'}"
                internal_issues += 1
            elif frag:
                ids = file_ids(target, id_cache)
                # Also accept <a name="..."> anchors.
                if frag not in ids:
                    status, err = "broken-anchor", f"#{frag} not found in {target.relative_to(ROOT)}"
                    internal_issues += 1
            results.append({"url": href, "source": rel, "item": path.name,
                            "kind": "internal", "status": status,
                            "statusCode": code, "error": err})

    # --- 2. Index-derived URLs (public-index + source-link-index) -----------
    for item in load(DOCS / "public-index.json", {}).get("items", []):
        for key in ("url", "repoUrl", "docsUrl", "pageUrl"):
            val = item.get(key)
            if not val:
                continue
            if val.startswith("http"):
                if is_loopback(val) or is_extraction_artifact(val):
                    continue
                # Same-site URLs are verified against this checkout (see §1).
                if val.startswith(BASE + "/"):
                    local = urllib.parse.unquote(val[len(BASE) + 1:].split("#", 1)[0].split("?", 1)[0])
                    target = DOCS / local
                    if target.is_dir():
                        target = target / "index.html"
                    internal_checked += 1
                    if not target.exists():
                        internal_issues += 1
                        results.append({"url": val, "source": "public-index", "item": item.get("name", ""),
                                        "kind": "internal", "status": "broken-internal",
                                        "statusCode": None, "error": f"same-site target missing locally: {local}"})
                    else:
                        results.append({"url": val, "source": "public-index", "item": item.get("name", ""),
                                        "kind": "internal", "status": "ok",
                                        "statusCode": None, "error": ""})
                    continue
                add(val, "public-index", item.get("name", ""), "external")
            else:
                # Repo-relative file reference (e.g. a docsUrl that is a bare
                # filename): verify the file exists in the checkout.
                target = (ROOT / val).resolve()
                internal_checked += 1
                try:
                    target.relative_to(ROOT.resolve())
                    exists = target.exists()
                except ValueError:
                    exists = False
                if not exists:
                    internal_issues += 1
                    results.append({"url": val, "source": "public-index", "item": item.get("name", ""),
                                    "kind": "internal", "status": "broken-internal",
                                    "statusCode": None, "error": "repo file does not exist"})
                else:
                    results.append({"url": val, "source": "public-index", "item": item.get("name", ""),
                                    "kind": "internal", "status": "ok",
                                    "statusCode": None, "error": ""})
    skipped_meta = 0
    for link in load(DOCS / "source-link-index.json", {}).get("links", []):
        url = link.get("url", "")
        if not url.startswith("http"):
            continue
        # Meta-records: links the old report *checked*, extracted from the
        # report file itself — not links the site contains. Skip, don't chase.
        if link.get("sourcePath") in ("docs/LINK_CHECK_REPORT.json", "LINK_CHECK_REPORT.json"):
            skipped_meta += 1
            continue
        # Historical snapshots: artifacts/ backups and diagnostics are frozen
        # history, not live site content.
        if (link.get("sourcePath") or "").startswith("artifacts/"):
            skipped_meta += 1
            continue
        if "{" in url or "}" in url:
            continue
        host = urllib.parse.urlparse(url).hostname or ""
        if host in PLACEHOLDER_HOSTS:
            continue
        if is_loopback(url) or is_extraction_artifact(url):
            continue
        # Same-site URLs are verified against this checkout (see §1).
        # Records in the source-link-index are historical cross-repo metadata,
        # not live site links: a missing target means the index is stale
        # (e.g. pages deleted in the Fix 5 orphan cleanup), not that the
        # live site is broken. Recorded as stale, not counted as an issue.
        if url.startswith(BASE + "/"):
            local = urllib.parse.unquote(url[len(BASE) + 1:].split("#", 1)[0].split("?", 1)[0])
            target = DOCS / local
            if target.is_dir():
                target = target / "index.html"
            internal_checked += 1
            if not target.exists():
                results.append({"url": url, "source": "source-link-index", "item": link.get("repoName", ""),
                                "kind": "internal-index", "status": "stale-index",
                                "statusCode": None, "error": f"stale index record; target not in current site: {local}"})
            else:
                results.append({"url": url, "source": "source-link-index", "item": link.get("repoName", ""),
                                "kind": "internal-index", "status": "ok",
                                "statusCode": None, "error": ""})
            continue
        add(url, "source-link-index", link.get("repoName", ""), "external-index")

    # --- 3. Fetch external URLs --------------------------------------------
    # Live-site links (kind "external") decide the exit code. Source-link-index
    # records (kind "external-index") are historical cross-repo metadata: they
    # are still fetched and reported, but counted separately so a stale index
    # record cannot fail a clean live site.
    external = [r for r in results if r.get("kind") in ("external", "external-index")]
    external = external[:MAX]
    external_checked = external_blocked = external_issues = 0
    index_record_issues = 0
    if FETCH and external:
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futures = {pool.submit(check_external, r["url"]): r for r in external}
            for fut in as_completed(futures):
                rec = futures[fut]
                status, code, err = fut.result()
                rec["status"] = status
                rec["statusCode"] = code
                rec["error"] = err
                external_checked += 1
                if status == "blocked":
                    external_blocked += 1
                elif status != "ok":
                    if rec["kind"] == "external-index":
                        index_record_issues += 1
                    else:
                        external_issues += 1
    elif external:
        for rec in external:
            rec["status"] = "skipped"
            rec["statusCode"] = None
            rec["error"] = "external fetch disabled (CHECK_EXTERNAL_LINKS=0)"

    # A bare origin (https://host with no path) that fails while other URLs
    # on the same origin succeed is an API base with no root route, not a
    # broken link — the origin is alive; it just serves endpoints, not /.
    if FETCH:
        live_origins = {urllib.parse.urlparse(r["url"]).netloc
                        for r in results if r.get("status") == "ok"}
        for rec in external:
            if rec["status"] in ("http-error", "fetch-error"):
                parsed = urllib.parse.urlparse(rec["url"])
                if parsed.path in ("", "/") and parsed.netloc in live_origins:
                    rec["status"] = "skipped"
                    rec["error"] = "bare API origin with no root route; endpoints on this origin respond"
                    if rec["kind"] == "external-index":
                        index_record_issues -= 1
                    else:
                        external_issues -= 1

    issues = internal_issues + external_issues
    checked = internal_checked + external_checked
    skipped_external = sum(1 for r in results if r.get("status") == "skipped")
    out = {
        "schemaVersion": "1.0",
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": "live" if FETCH else "offline-format",
        "totalLinks": len(results),
        "checked": checked,
        "skippedExternal": skipped_external,
        "issues": issues,
        "liveIssues": issues,
        "indexRecordIssues": index_record_issues,
        "internalLinks": internal_checked,
        "internalChecked": internal_checked,
        "internalIssues": internal_issues,
        "externalLinks": len(external),
        "externalChecked": external_checked,
        "externalBlocked": external_blocked,
        "externalIssues": external_issues,
        "skippedMetaRecords": skipped_meta,
        "durationSeconds": round(time.time() - started, 1),
        "timeoutPolicy": {
            "mode": "generation-based",
            "secondsPerLink": TIMEOUT,
            "maxLinks": MAX,
            "workers": WORKERS,
        },
        "results": results,
    }
    (DOCS / "LINK_CHECK_REPORT.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"LINK CHECK {'OK' if issues == 0 else 'ISSUES'}: {len(results)} links "
          f"({internal_checked} internal, {len(external)} external), "
          f"{issues} live issues ({internal_issues} internal, {external_issues} external), "
          f"{index_record_issues} stale source-link-index issues, "
          f"{external_blocked} blocked (rate-limited), mode={out['mode']}")
    return 1 if issues and FETCH else 0


if __name__ == "__main__":
    raise SystemExit(main())
