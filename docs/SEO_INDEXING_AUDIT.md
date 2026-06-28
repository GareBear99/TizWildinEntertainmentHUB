# SEO Indexing Audit — Static Public Link Layer

## Purpose

This pass upgrades the GitHub Pages HUB from an interactive dashboard only into a crawlable public ecosystem index. The goal is to make every major TizWildin / GareBear99 / ARC route discoverable through direct links, static HTML, JSON, Markdown, sitemap, robots, and LLM-friendly text.

## Added index surfaces

- `ecosystem-index.html` — full static public ecosystem page.
- `arc-index.html` — ARC source-spine route page.
- `pages/*.html` — individual static route pages for plugins, packs, lists, and ARC routes.
- `public-index.json` — machine-readable catalog.
- `llms.txt` — compact LLM/search-assistant index.
- `PUBLIC_LINK_GRAPH.md` — GitHub-readable route graph.
- `sitemap.xml` — generated sitemap including static detail pages.
- `robots.txt` — allows crawlers and points to sitemap.

## Updated source manifests

- `lists.json` now includes an `ARC Source Spine` category.
- ARC public routes added: ARC-Neuron-LLMBuilder, ARC-Core, arc-lucifer-cleanroom-runtime, arc-language-module, Arc-RAR, OmniBinary Runtime.

## Indexing doctrine

1. Keep `plugins.json`, `packs.json`, and `lists.json` as the public source of truth.
2. Regenerate the static layer with `python3 scripts/build_public_index.py`.
3. Keep GitHub Pages links direct and absolute where possible.
4. Avoid JavaScript-only discovery for key public routes.
5. Use static HTML + JSON-LD + sitemap for search-friendly crawling.
6. Use `llms.txt` and `public-index.json` for AI crawlers, assistants, and future internal tooling.

## Verification checklist

- JSON manifests parse successfully.
- Static index builds without errors.
- Sitemap includes the dashboard, SEO page, ecosystem index, ARC index, JSON index, LLM index, and individual pages.
- Dashboard links to the new public indexes.
- Repo README documents regeneration workflow.

## v7 Completion Pass — Static Index Hardening

This pass upgrades the HUB from a simple public route layer into a repeatable static indexing system.

### Added

- Dedicated static route page for every indexed plugin, pack, public list, ARC source-spine repo, and submission route.
- Per-route canonical URL, description, OpenGraph metadata, Twitter card metadata, and JSON-LD structured data.
- Generated SVG social cards under `docs/assets/social/` for the HUB and every route page.
- `docs/public-index.json` schema version `2.0` with IDs, route pages, canonical URLs, repository URLs, docs URLs, languages, licenses, source manifest fields, and tags.
- `docs/schemas/public-index.schema.json` for machine-readable index structure.
- `docs/SEO_BUILD_REPORT.json` for generated counts and build evidence.
- CI workflow `.github/workflows/public-index.yml` to rebuild and validate the public index on push/PR.
- Offline validator `scripts/validate_public_index.py` to fail on missing pages, missing metadata, broken sitemap-local targets, invalid JSON, missing critical graph entries, or dev/cache artifacts.

### Current validated build

- Indexed records: 52
- Static route pages: 52
- Sitemap URLs: 113
- Generated social cards: 53
- Critical routes verified: FreeEQ8, ARC-Core, Public Credibility SEO Tracker

### Remaining external-only work

The validator intentionally does not perform live network crawling during local package builds. Live external HTTP checks should be performed after pushing to GitHub Pages so the final deployed URLs can be verified against real public responses.
