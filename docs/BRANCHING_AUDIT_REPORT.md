# Branching Audit Report

Status: **Branch governance layer added and validated.**

## Correction (2026-11-07, Branch 1 `seo/public-index-v8-branching`)

The earlier version of this report listed `.github/workflows/branch-discipline.yml`, `.github/pull_request_template.md`, and `.github/ISSUE_TEMPLATE/branch-task.md` as added. They were not in the repo — no git history for any of them, and `.github/` contained only `hub-build.yml` and `itch-inventory-refresh.yml`. All three files were created on Branch 1. Everything else below was verified present on `main` at `c987fe8`.

## Added

- `docs/branch-map.json` — machine-readable branch topology and queue.
- `docs/BRANCHING_STRATEGY.md` — canonical branch workflow.
- `docs/BRANCH_EXECUTION_QUEUE.md` — current branch execution order.
- `docs/BRANCH_PROTECTION_RULES.md` — recommended GitHub protection rules.
- `docs/BRANCH_RELEASE_LADDER.md` — release and hotfix merge ladder.
- `scripts/validate_branch_map.py` — branch governance validator.
- `.github/workflows/branch-discipline.yml` — CI validation for branch map + public index. (Added on Branch 1; was missing despite this report previously claiming it.)
- `.github/pull_request_template.md` — PR checklist for branch discipline. (Added on Branch 1; was missing.)
- `.github/ISSUE_TEMPLATE/branch-task.md` — branch task issue template. (Added on Branch 1; was missing.)
- Public route pages for branching, SEO branch, LibHunt branch, ARC branch, audio branch, and release branch through the static generator.

## Validated

```text
python scripts/build_public_index.py
python scripts/validate_public_index.py
python scripts/validate_branch_map.py
```

Last validation output (Branch 1, 2026-11-07, on `seo/public-index-v8-branching`):

```text
Built public index: 220 records, 462 sitemap URLs, 174 social cards, 54 orphan pages reported
VALIDATION OK: 220 items, 462 sitemap URLs, 220 route pages
BRANCH MAP VALIDATION OK: 9 tracked branches
```

Branch 1 status: branch `seo/public-index-v8-branching` exists and is in progress (`docs/branch-map.json` status updated from `next` to `in-progress`). Merge target per the ladder is `develop`, which does not exist — whether to practice the `develop` ladder or drop it is Gary's call; do not create `develop` without his say-so.

## Next branch to open

```text
submission/libhunt-arc-graph
```

Goal: finish the ARC LibHunt alternatives graph:

```text
ARC-Neuron-LLMBuilder ↔ ARC-Core ↔ arc-lucifer-cleanroom-runtime ↔ arc-language-module ↔ Arc-RAR
```

Then open:

```text
submission/libhunt-tizwildin-audio-graph
```

Goal: finish the TizWildin audio LibHunt alternatives graph:

```text
FreeEQ8 ↔ TizWildinEntertainmentHUB ↔ FreeVox8 ↔ awesome-audio-plugins-dev
```
