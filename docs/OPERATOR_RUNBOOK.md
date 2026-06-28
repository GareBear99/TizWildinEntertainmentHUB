# Operator Runbook

## Daily / change-based checks

```bash
python scripts/validate_repo.py
python -m compileall -q arc_service/app scripts
```

## API check

```bash
cd arc_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
uvicorn app.main:app --reload
```

## Add a plugin

1. Edit `plugins.json`.
2. Copy/verify the entry is reflected on GitHub Pages.
3. Run `python scripts/validate_repo.py`.
4. Commit with message: `catalog: add <plugin-name>`.

## Add a pack

1. Edit `packs.json`.
2. Add proof/download status honestly.
3. Run validation.
4. Commit with message: `catalog: add <pack-name>`.

## Release artifact rule

Do not commit generated zips in `artifacts/staged/`. Generate or import release artifacts during the local/runtime release process, then attach real builds to GitHub Releases.
