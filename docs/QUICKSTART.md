# TizWildinEntertainment HUB Quickstart

## Fast local demo
1. Start ARC:
   `./scripts/run_arc_demo.sh`
2. Bootstrap demo data:
   `curl -X POST "http://127.0.0.1:8000/demo/bootstrap?stage_artifacts=true"`
3. Open these useful endpoints:
   - `/launchpad/demo_account?machine_id=mac_demo&channel=stable`
   - `/account-summary/demo_account`
   - `/catalog/owned/demo_account`
   - `/releases`

## Docker route
Run:
`docker compose up --build`

Then bootstrap the same way.

## What v1.0 adds
- one-shot demo bootstrap
- consolidated launchpad endpoint
- Dockerfile + compose
- cleaner local run path
- richer machine summaries with product counts


### Extra operator endpoints
- `POST /sync` for a one-call readiness and install/download summary
- `GET /audit/{account_id}` for a quick readiness score
- `GET /support/bundle/{account_id}` to write a support zip with diagnostics + backup


## New in v1.3
- `POST /auth/register` creates a local user and seeds entitlements/settings.
- `POST /auth/login` returns access + refresh tokens.
- `POST /auth/refresh` rotates a new access token.
- `POST /billing/checkout-session` creates a local checkout intent.
- `POST /billing/checkout-complete` mutates entitlements for testing purchases.
- `POST /releases/import` imports release manifests from a JSON file path, `file://`, or URL.
