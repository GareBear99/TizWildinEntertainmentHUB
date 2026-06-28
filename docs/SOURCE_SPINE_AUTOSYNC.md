# Source Spine Autosync

The public Hub now treats the dashboard manifests as the source of truth for the ecosystem graph.

## Public source of truth

- `plugins.json` — audio plugins and creator tools
- `packs.json` — sample packs and producer kits
- `lists.json` — discovery lists, public routes, ARC routes, Release Vault, and all-links routes
- `docs/source-repos.json` — generated source-spine repository registry

## Workflow

Add or update an entry in `plugins.json`, `packs.json`, or `lists.json`, then run:

```bash
python scripts/sync_source_spine_from_manifests.py
python scripts/build_public_index.py
python scripts/build_source_repo_index.py
python scripts/build_search_index.py
python scripts/check_public_links.py
python scripts/score_repository_readiness.py
python scripts/build_index_health.py
```

For local archive hydration during a deep release pass, pass source overrides:

```bash
python scripts/build_source_repo_index.py \
  --repo tizwildin-release-vault=/path/to/TizWildin-Release-Vault.zip \
  --repo arc-core=/path/to/ARC-Core.zip \
  --repo arc-rar=/path/to/Arc-RAR.zip \
  --repo omnibinary-runtime=/path/to/omnibinary-runtime.zip
```

For GitHub API hydration where network access is available:

```bash
SOURCE_INDEX_FETCH_REMOTE=1 python scripts/build_source_repo_index.py
```

## What gets generated

- `docs/public-index.json`
- `docs/source-index.json`
- `docs/source-link-index.json`
- `docs/search-index.json`
- `docs/repo-file-search.html`
- `docs/search.html`
- `docs/index-health.html`
- `docs/repo-readiness.html`
- `docs/pages/*.html`
- `docs/sitemap.xml`
- `docs/llms.txt`

## Current link policy

The FFM Bio route is the primary all-links route:

https://ffm.bio/no4km87

It is included in:

- `lists.json`
- `docs/data/lists.json`
- generated public index
- generated search index
- extracted source link graph
- sitemap / route generation

## Design rule

Adding another public project should be a manifest update, not a manual rebuild of static pages.
The generators create route pages, index records, search records, source-spine entries, and link-graph records from the manifests.
