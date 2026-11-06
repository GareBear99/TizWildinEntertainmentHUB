
## 2026-11-05 — Itch inventory, ProEQ8 catalog, Cloudflare inventory

- Added the 4 live audio packs to the itch inventory (107 → 111 items): 808 Producer Kit ($1.37 CAD), Subwoofer Crown Bass Pack (free), Violin Synth Sample Kit ($2.50 CAD), A Devil's Game – Hellfire Arena Kit ($2.10 CAD). The itch refresh run that followed (17:22 UTC) enriched 3 of the 4 with live covers/descriptions; A Devil's Game detail fetch hit itch rate-limiting (HTTP 429) and kept its manual entry plus a profile fallback.
- Made ProEQ8 visible in the catalog as the commercial pro EQ; fixed the live site loading its own data (JSONs at the site URL, relative fetches); consolidated the catalog to one source of truth; moved Therum to dev; corrected the DAFx26 claim and the Riser count.
- Account page now sends its session token on account reads (ready for the fixed tizwildin-hub worker v3.2.0).
- Added `CLOUDFLARE.md`: worker inventory, repo mapping, and live ping results for the Cloudflare account.

## 2026-05-03 — V1 Start Here List Routing Update

- Promoted `awesome-audio-plugins-dev` as the canonical **Start Here** list on the default public V1 dashboard.
- Added/retained visible public routing to `awesome-audio-lists`, `awesome-music-platforms`, and `awesome-python-audio-science`.
- Updated `lists.json` and `docs/data/lists.json` with priority ordering, Start Here metadata, and Python audio science routing.
- Updated `docs/index.html` and `docs/index-seo.html` so the `.io` public page exposes crawlable links to the complete list network.
- Added audit evidence under `docs/V1_START_HERE_LIST_AUDIT.md`.

# Changelog

## 2026-05-04 — V1 public dashboard Lists tab + discovery network routing

- Added a visible **📚 Lists** tab to the default public `.io` dashboard (`docs/index.html`).
- Added `lists.json` and `docs/data/lists.json` as the data source for canonical list/project anchors.
- Linked the HUB to `awesome-audio-lists`, `awesome-music-platforms`, `awesome-audio-plugins-dev`, FreeEQ8, FreeVox8, and Release Vault.
- Updated the SEO landing page, sitemap, README, and audit docs to reflect the list-network routing.
- Preserved V1 default behavior and the auto-check toggle default.


## v2.0.0 — Public production hardening audit

- Rebuilt README as a public SEO and trust funnel.
- Rebuilt GitHub Pages landing page with stronger hero, metadata, local catalog loading, and explicit production stance.
- Added `scripts/validate_repo.py` as a hard public-readiness gate.
- Added engineering audit, SEO traction plan, and operator runbook docs.
- Added static docs catalog copies under `docs/data/`.
- Fixed empty sitemap and empty catalog issue template.
- Removed generated staged artifact zips from the public package.
- Reset stale local runtime mock state.
- Synced API product catalog with root product manifest.
- Fixed audit receipt count source.
- Fixed uninstall CURRENT pointer cleanup.
- Hardened plugin bridge approval parsing.
- Tightened `.gitignore` for runtime/build/secrets/generated artifacts.

## v1.0.0 — SEO hub baseline

- Public hub scaffold for plugins, packs, Release Vault routing, docs, and local API/app planning.
