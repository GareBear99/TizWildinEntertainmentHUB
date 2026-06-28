# Source Indexing System

The Hub now has a static source-repository index layer. The goal is simple: one new repository entry should be enough to generate route pages, searchable file records, extracted links, and public discovery metadata.

## Add a repository

Edit `docs/source-repos.json` and add one object to `repositories`:

```json
{
  "id": "example-repo",
  "name": "Example Repo",
  "cluster": "TizWildin Audio Plugins",
  "url": "https://github.com/GareBear99/example-repo",
  "docs": "https://github.com/GareBear99/example-repo#readme",
  "sourceType": "archive-or-clone",
  "path": "source_archives/example-repo.zip",
  "priority": 20,
  "tags": ["audio-plugin", "open-source"]
}
```

Then run:

```bash
python scripts/build_source_repo_index.py
python scripts/validate_source_index.py
python scripts/benchmark_public_index.py
```

## Local archive override

For local builds, point the generator at uploaded zips or cloned folders without committing large archives:

```bash
python scripts/build_source_repo_index.py \
  --repo arc-core=/path/to/ARC-Core-main.zip \
  --repo arc-rar=/path/to/Arc-RAR-main.zip
```

## Generated outputs

- `docs/source-index.json` — searchable file records
- `docs/source-link-index.json` — extracted link graph
- `docs/repo-file-search.html` — static browser search UI
- `docs/SOURCE_REPOSITORY_INDEX.md` — human-readable source index
- `docs/pages/source-*.html` — per-repo source pages

## Timeout policy

Timeouts are generation-based. The source indexer reads the configured policy in `docs/source-repos.json` and calculates a build budget from repository count and expected scale. Override with `SOURCE_INDEX_TIMEOUT_SECONDS` for large local audits.
