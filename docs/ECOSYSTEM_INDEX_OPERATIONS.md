# Ecosystem Index Operations

This repository now treats the HUB as a public ecosystem index, not only a landing page.

## Add a new repo

1. Add one record to `docs/source-repos.json`.
2. Run `python scripts/build_source_repo_index.py`.
3. Run `python scripts/build_search_index.py`.
4. Run `python scripts/score_repository_readiness.py`.
5. Run `python scripts/build_index_health.py`.
6. Commit generated JSON, HTML, sitemap, and report changes.

## Public routes

- `docs/index-health.html` summarizes current index health.
- `docs/search.html` searches public routes, files, and links.
- `docs/repo-readiness.html` grades indexed repositories for public submission readiness.
- `docs/repo-file-search.html` searches files and links by source repository.

## Timeout policy

Source indexing and link checking use generation-based limits so large repo graphs can grow without silent hangs. For live checks, set `CHECK_EXTERNAL_LINKS=1`. The default mode verifies URL format only so CI remains reliable without network dependency.
