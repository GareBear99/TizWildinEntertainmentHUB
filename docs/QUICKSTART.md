# Quickstart

## View the public site

```bash
python3 -m http.server 8080
# open http://localhost:8080/docs/
```

## Run the local API

```bash
cd arc_service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Run tests

```bash
cd arc_service
python -m pytest
```

## Important public-facing note

This repo contains production-facing docs and scaffolding, but checkout/account systems should only be described as live after real infrastructure, secrets, payment providers, signed builds, and deployment controls are connected.
