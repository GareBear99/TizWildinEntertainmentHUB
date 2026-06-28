# Public Index Top-Tier Readiness

This Hub is designed as a public-facing source, link, and ecosystem index for the GareBear99 / TizWildin / ARC project graph.

## Current top-tier requirements

- Public wording is professional and production-facing.
- Every indexed project has a route page, sitemap entry, and search presence.
- Source repositories can be added through `docs/source-repos.json`.
- Local folders, zip archives, and optional GitHub API hydration are supported.
- The source index extracts repository files, summaries, query text, and outbound links.
- The repository search page can query files and links across the indexed graph.
- Validation fails if public index output contains non-public audit branding.
- Benchmark reports are generated into `docs/PUBLIC_INDEX_BENCHMARK.json`.

## Adding a new source repo

1. Add one object to `docs/source-repos.json`.
2. Use `sourceType: remote-url` for a GitHub-only record, or add a local path/archive when available.
3. Run:

```bash
python scripts/build_public_index.py
python scripts/build_source_repo_index.py
python scripts/validate_public_index.py
python scripts/validate_source_index.py
python scripts/benchmark_public_index.py
```

Optional GitHub hydration:

```bash
SOURCE_INDEX_FETCH_REMOTE=1 python scripts/build_source_repo_index.py
```

## Grade target

The current target is A- or better: complete validation, route generation, source search, link extraction, and acceptable generation time.
