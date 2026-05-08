# Branching Strategy

This repository now treats public SEO/indexing work as a repeatable branch-based operating system instead of one-off edits.

## Canonical branch ladder

| Branch | Role | Merge target |
|---|---|---|
| `main` | Protected public release branch for GitHub Pages and stable releases. | N/A |
| `develop` | Integration branch for validated route/index/doc work before release. | `main` through release branch |
| `seo/*` | Sitemap, route pages, schema, social cards, metadata, link graph, LLM index. | `develop` |
| `submission/*` | LibHunt, Open Hub, SourceForge, AlternativeTo, awesome-list evidence and submission records. | `develop` |
| `route/*` | Platform-specific route preparation: GitHub Topics, Open Hub, SourceForge, awesome lists, audio directories. | `develop` |
| `arc/*` | ARC source-spine route and local AI submission work. | `develop` |
| `audio/*` | TizWildin audio/plugin/sample-pack/listing route work. | `develop` |
| `release/*` | Frozen candidate after validation passes. | `main` |
| `hotfix/*` | Broken link, JSON, sitemap, route, or metadata emergency fix. | `main` and back-merge to `develop` |

## Current working branch

`seo/public-index-v8-branching`

Purpose: add branch governance, branch-map data, branch validation, and public branch route pages so the ecosystem can scale like GitHub-style indexed project infrastructure.

## Required checks before merge

```bash
python scripts/build_public_index.py
python scripts/validate_public_index.py
python scripts/validate_branch_map.py
```

## Operating doctrine

- Source manifests and docs are edited first.
- The static public index is rebuilt second.
- Validators run third.
- Evidence notes are saved for directory/list submissions.
- `main` only receives validated release/hotfix changes.
- The HUB remains the public front door; tracker/submission repos remain the evidence ledger.

## Immediate branch queue

1. `submission/libhunt-arc-graph` — finish ARC LibHunt alternatives.
2. `submission/libhunt-tizwildin-audio-graph` — finish FreeEQ8/HUB/FreeVox8/audio list graph.
3. `route/github-topics-cleanup` — normalize GitHub topics across first-wave repos.
4. `route/openhub-sourceforge` — prepare external open-source directory records.
5. `route/awesome-lists` — prepare PR-ready awesome-list submissions.
6. `arc/source-spine-index` — deepen ARC source-spine public route pages.
7. `audio/tizwildin-directory-index` — deepen audio/plugin/sample-pack route pages.
8. `release/public-index-v8` — freeze and ship after validation.
