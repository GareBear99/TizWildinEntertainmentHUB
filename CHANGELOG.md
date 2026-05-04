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
