# Deferred Cut Proposal — TizWildinEntertainmentHUB

**Status: PROPOSAL ONLY — nothing in this document has been deleted, and nothing
here should be deleted without Gary's explicit approval per item.**
Prepared 2026-11-05. Counts verified against the repo (see Verification below).

Cutting means removing the item from the repo and the published site (and, for
pages, from the sitemap/index). Before any cut, confirm nothing external links
to the item — the orphan report's own note says the same.

## 1. Orphan pages — 63

**Where:** `docs/pages/*.html`, listed in `docs/ORPHAN_PAGES_REPORT.json`
(generated 2026-11-05). **Verified count: 63** — an independent recount
(files in `docs/pages/` present in neither `docs/sitemap.xml` nor
`docs/public-index.json`) returns exactly the same 63 filenames.

Breakdown:

| Group | Count | Examples |
|---|---|---|
| `tizwildin-audio-plugins-*` | 19 | `tizwildin-audio-plugins-freeeq8.html`, `-aether`, `-bassmaid`, `-chainmaid`, `-freesampler`, `-gluemaid`, `-instrudio`, `-metermaid`, `-mixmaid`, `-multimaid` |
| `discovery-lists-and-public-routes-*` | 15 | `…-freeeq8`, `…-freevox8`, `…-awesome-audio-lists`, `…-tizwildin-release-vault`, `…-arc-core` |
| `tizwildin-sample-packs-*` | 11 | `…-free-808-producer-kit`, `…-free-dark-piano-sound-kit`, `…-free-riser-producer-kit`, `…-phonk-producer-toolkit`, `…-tizwildin-aurora/chime/chroma/obsidian/skyline` |
| `itch-*` (generated route pages) | 9 | `itch-arcanum-i-part-3-…`, `itch-arcanum-iii-vanta-abilities`, `itch-coin-physics-pack-…`, `itch-cool-backdrop-layers-engine`, `itch-crawl-space-svg-…`, `itch-dark-fantasy-modular-gui-pack-…`, `itch-enchanted-sprite-fx-engine`, `itch-menu-panels`, `itch-slagworks-4-map-…` |
| `arc-source-spine-*` | 6 | `arc-source-spine-arc-core`, `…-arc-rar`, `…-omnibinary-runtime`, `…-arc-language-module`, `…-arc-neuron-llmbuilder`, `…-arc-lucifer-cleanroom-runtime` |
| Core pages (see warning) | 3 | `account.html`, `api.html`, `docs.html` |

**Why cuttable (the 60):** generated route/index pages for items that are
already covered by the public index, the itch inventory, or the catalog — or
for planned items with no live content behind them. They are not linked from
the sitemap or the public index, so no in-site navigation reaches them.

**⚠️ DO NOT CUT the 3 core pages:** `docs/pages/account.html`,
`docs/pages/api.html`, and `docs/pages/docs.html` are the live HUB account
page, API reference, and docs landing page. Their "orphan" status is an
index/sitemap gap — the fix is to link them from the index/sitemap, not to
delete them. Cutting them would remove the working account UI and API docs.

**⚠️ Check before cutting the 11 sample-pack pages:** five of them
(808 Producer Kit, Dark Piano, Future Bass, Riser, Violin Synth) name packs
that are in `packs.json` as prepped-but-unpublished; the itch inventory work
(2026-11-05) added the live versions of 808/Violin to `all_items.json`. If a
pack later goes live on itch, its route page may be wanted back — the
generator (`scripts/build_public_index.py`) can recreate route pages, so a
cut is recoverable as long as the generator still covers them.

## 2. Placeholder games — 4

**Where:** `games.json` + `docs/games.json`, entries with `status: "planned"`,
no `repo`, no `demoUrl`, description "Coming soon — …".

| Game | Description |
|---|---|
| WraithEternal | "dark action game route … reserved for future playable builds" |
| SlimeVeil | "stylized slime-horror game route for future demos" |
| ThingsHappening | "experimental game route for future public demos" |
| M.O.M | "M.O.M game route reserved for future playable builds" |

**Why cuttable:** placeholders with no code, no demo, no repo — they exist
only to reserve a name/route. **Not candidates:** RiftAscent and Neolution
(`status: "alpha"`, live demo URLs at `garebear99.github.io/RiftAscent/` and
`/Neolution/`) — those are real, playable games.

## 3. SlushAI — 1 planned tool

**Where:** `tools.json` (`id: "slushai"`, `status: "planned"`, `repo: ""`),
`docs/pages/slushai.html`, public-index entry (`status: "planned"`,
`priority: 35`, no `url`/`docs`).

**What it is:** "Coming soon — AI-assisted creator automation tool for the
TizWildin ecosystem, intended for prompt-driven music, media, and release
workflow support." No code, no repo, no live URL.

**Why cuttable:** a "coming soon" stub advertising a tool that does not
exist. Cutting = removing the `tools.json` entry, the route page, and the
public-index entry. Re-adding later is a one-entry change when the tool is
real.

## 4. Tutorials — empty section

**Where:** `tutorials.json` and `docs/tutorials.json`.

**What it is:** a tutorials section with 4 categories (Getting Started,
Plugin Development, Music Production, Ecosystem & Tools) and
**zero tutorials** (`"tutorials": []` in both copies). No tutorial pages
exist in `docs/pages/`.

**Why cuttable:** an empty section — categories with nothing in them. Cutting
= removing the two JSON files (and any nav pointing at tutorials). The
categories can be recreated when the first real tutorial exists.

## 5. Sponsor Platform — plan only, no code

**Where:** `FUTURE_PLANS.md` §1 "Launch the Sponsor Platform" (lines ~24–90,
plus mentions at lines 109, 191, 207–219, 362, 365, 390, 394, 425).

**What it is:** a strategy document for a SaaS-style sponsor/monetization
layer (developer licenses, update channels, repo-generation tools, sponsor
tiers for early access/stems/packs/beta tools). There is no Sponsor Platform
code, page, or product in the repo. The "Sponsor" links in the live pages
(`docs/index.html`, `docs/pages/account.html`, `docs/pages/docs.html`) are
plain outbound links to `github.com/sponsors/GareBear99` — GitHub Sponsors,
not a platform — and are **not** part of this cut.

**Why cuttable:** deferring the plan means striking or parking the
FUTURE_PLANS.md §1 section (and its scattered mentions) so the roadmap stops
promising a platform with no owner, timeline, or code. It is a docs-only cut.

## 6. JUCE desktop app — two scaffolds, no app

**Where:** `hub_app/` (12 files, 68K) and `hub_scaffold/` (9 files, 36K).

- `hub_app/`: `CMakeLists.txt`, `README.md` ("This JUCE app is still a
  scaffold, but v0.4 is now pointed at a richer ARC backend surface…"),
  `Source/` — `HubProcessor`, `HubEditor`, `TizHubMainComponent`,
  `GitHubClient`, `HubSettings`, `PluginManifest`.
- `hub_scaffold/`: `README.md` ("This is a file-level scaffold for the JUCE
  desktop hub app."), `Source/` — `Main.cpp`, `TizHubApplication`,
  `TizHubMainComponent`, `ArcClient`, `TizHubState`.

**Why cuttable:** two overlapping scaffolds for a desktop hub app that has
never been built or shipped; the HUB itself is the GitHub Pages site
(`docs/`) plus the Cloudflare worker. Cutting = removing both directories
(after confirming no CI or doc references them — see Verification). Keeping
one scaffold and deleting the other is also an option if Gary wants to keep
the desktop-app idea alive.

## Verification (how the numbers were checked)

- Orphan pages: `docs/ORPHAN_PAGES_REPORT.json` says 63; independent recount
  (files in `docs/pages/` in neither `docs/sitemap.xml` nor
  `docs/public-index.json`) returns the same 63 filenames, and all 63 exist
  on disk. Sitemap has 446 `<loc>` entries; `docs/pages/` has 326 files.
- Placeholder games: `games.json` has 6 games — 2 alpha with live demo URLs
  (RiftAscent, Neolution), 4 planned with empty repo/demoUrl.
- SlushAI: `tools.json` + public-index both `status: "planned"`, empty repo.
- Tutorials: `"tutorials": []` in both `tutorials.json` and
  `docs/tutorials.json`.
- Sponsor Platform: `grep` finds it only in `FUTURE_PLANS.md` (plan text) and
  as outbound GitHub Sponsors links in 3 pages.
- JUCE app: `find hub_app hub_scaffold -type f` = 21 files total.

## What this proposal does NOT cover

- The Cloudflare dead workers/Pages/D1 (`botfortress`, `botfortress-api`,
  `botfortress-web`, `botfortress` Pages) — those are recorded in
  `CLOUDFLARE.md` under "Decisions owed", not here.
- The 3 core orphan pages (`account.html`, `api.html`, `docs.html`) — link
  them, do not cut them.
- Anything live: the itch inventory (111 items), the catalog, the account
  page, the worker docs.
