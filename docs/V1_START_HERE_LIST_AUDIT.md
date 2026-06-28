# V1 Start Here List Audit

Date: 2026-05-03

## Intent

Promote `awesome-audio-plugins-dev` as the default public ecosystem **Start Here** list from the TizWildinEntertainmentHUB `.io` V1 page, while preserving the existing plugin and pack dashboard behavior.

## Files audited / updated

- `docs/index.html` — default V1 dashboard. Added Start Here note, featured list-card styling, header route, and prioritized list rendering.
- `docs/index-seo.html` — SEO landing page. Added crawlable Start Here section and Python audio science route.
- `lists.json` — root public list manifest. Added `start_here` category, Start Here metadata, and `awesome-python-audio-science`.
- `docs/data/lists.json` — mirrored Pages data manifest. Kept in sync with root `lists.json`.
- `README.md` — documented the Start Here role.
- `CHANGELOG.md` — added this release note.
- `docs/sitemap.xml` — updated with audit doc URL.
- `docs/FILE_INVENTORY.json` — regenerated after package update.

## Routing doctrine

`awesome-audio-plugins-dev` is now the first public list because it best captures the ecosystem's strongest search lane: free/open audio plugins, JUCE/VST3/AU development, DSP resources, FreeEQ8, FreeVox8, and producer/developer discovery.

Secondary routes remain available:

- `awesome-audio-lists` — parent hub and submission-target map.
- `awesome-music-platforms` — independent artist platforms, distribution, beat selling, sample packs, sync licensing, promotion, and storefronts.
- `awesome-python-audio-science` — Python scientific audio, MIR, DSP, ML audio, datasets, notebooks, and research/tooling.
- FreeEQ8 / FreeVox8 / Release Vault / TizWildin router surfaces.

## Non-regression checks

- `docs/index.html` remains the default V1 dashboard.
- Plugins tab remains default active tab.
- Packs tab remains intact.
- Lists tab remains read-only discovery/routing.
- Auto-check default remains ON for first-time users.
- No checkout, entitlement, or payment behavior was added.
