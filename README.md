# TizWildin Entertainment Hub + ARC Authority Layer

> **The central management plane for every TizWildin plugin — entitlements, seats, releases, and Stripe billing in one service.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/tests-20%20passing-brightgreen.svg)](#testing)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![Sponsor](https://img.shields.io/badge/sponsor-GareBear99-ea4aaa.svg)](https://github.com/sponsors/GareBear99)
[![Buy Me a Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-garebear99-FFDD00.svg)](https://buymeacoffee.com/garebear99)
[![Ko-fi](https://img.shields.io/badge/ko--fi-luciferai-FF5E5B.svg)](https://ko-fi.com/luciferai)

## What Is This?

TizWildin Entertainment Hub is the **authority + orchestration backend** for the TizWildin plugin ecosystem. It answers a single question for every plugin, on every machine, at every launch:

> **"Is this user allowed to run this product, on this machine, with these features?"**

The system is split into three layers:

```
┌─────────────────────────────────────────────────────────────┐
│  Stripe bills.   ARC decides.   Hub operates.   Plugins ask.│
└─────────────────────────────────────────────────────────────┘

┌──────────┐     ┌──────────────┐     ┌──────────────┐
│  Plugin   │────▶│   ARC Service │────▶│   SQLite DB   │
│  Bridge   │◀────│  (FastAPI)    │     │  (WAL mode)   │
└──────────┘     └──────┬───────┘     └──────────────┘
                        │
                        ├── GitHub Releases API (version polling)
                        └── Stripe Webhooks (payment events)

┌──────────────────────┐
│  Hub Desktop (JUCE)  │── browse / install / update / manage
└──────────────────────┘
```

**ARC** (Authority, Registry, Control) is the Python/FastAPI service at the heart of the system. It owns the canonical product catalog, entitlement records, seat allocations, receipts, and release state. The JUCE-based Hub desktop app and the thin plugin bridges are consumers of ARC's decisions — they never make authorization calls on their own.

## Product Catalog

The Hub manages **13 products** across **14 GitHub repositories**:

### Independent Headline Products
| Product | License | Price | Repo |
|---------|---------|-------|------|
| **FreeEQ8** | Free / Open | Free | [FreeEQ8](https://github.com/GareBear99/FreeEQ8) |
| **Therum** | Pro (Public Repo) | One-time | [Therum_JUCE-Plugin](https://github.com/GareBear99/Therum_JUCE-Plugin) |
| **WURP** | Pro (Public Repo) | One-time | [WURP_Toxic-Motion-Engine_JUCE](https://github.com/GareBear99/WURP_Toxic-Motion-Engine_JUCE) |
| **AETHER** | Pro (Public Repo) | One-time | [AETHER_Choir-Atmosphere-Designer](https://github.com/GareBear99/AETHER_Choir-Atmosphere-Designer) |
| **WhisperGate** | Free / Open | Free | [WhisperGate_Free-JUCE-Plugin](https://github.com/GareBear99/WhisperGate_Free-JUCE-Plugin) |
| **PaintMask** | Pro (Public Repo) | Sub / One-time | [PaintMask_Free-JUCE-Plugin](https://github.com/GareBear99/PaintMask_Free-JUCE-Plugin) |

### Maid Suite
| Product | License | Price | Repo |
|---------|---------|-------|------|
| **BassMaid** | Pro | One-time | [BassMaid](https://github.com/GareBear99/BassMaid) |
| **GlueMaid** | Pro | One-time | [GlueMaid](https://github.com/GareBear99/GlueMaid) |
| **SpaceMaid** | Pro | One-time | [SpaceMaid](https://github.com/GareBear99/SpaceMaid) |
| **MixMaid** | Pro | One-time | [MixMaid](https://github.com/GareBear99/MixMaid) |

### RiftWave Suite
| Product | License | Price | Repo |
|---------|---------|-------|------|
| **WaveForm / RiftSynth Lite** | Free Lite | Free | [RiftWaveSuite](https://github.com/GareBear99/RiftWaveSuite_RiftSynth_WaveForm_Lite) |
| **WaveForm Pro** | Pro | One-time | [RiftWaveSuite](https://github.com/GareBear99/RiftWaveSuite_RiftSynth_WaveForm_Lite) |
| **RiftSynth Pro** | Pro | One-time | [RiftWaveSuite](https://github.com/GareBear99/RiftWaveSuite_RiftSynth_WaveForm_Lite) |

### Complete Collection
Purchase all Pro products with a single "Owns Every VST" flag. Extra seats are **$3/month** each (max 9).

## Quick Start

### Prerequisites
- Python 3.11+
- pip

### Run the ARC service

```bash
git clone https://github.com/GareBear99/TizWildinEntertainmentHUB.git
cd TizWildinEntertainmentHUB/arc_service

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

ARC is now running at **http://127.0.0.1:8000**. Open http://127.0.0.1:8000/docs for the interactive Swagger UI.

### Seed mock data (optional)

```bash
python ../scripts/migrate_mock_to_db.py
```

This populates the SQLite database with sample accounts, entitlements, and seats for local development.

## API Reference

All endpoints are served under `http://127.0.0.1:8000` by default.

### Product Catalog

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/catalog` | Full product catalog with groups, editions, and repo slugs |

### Entitlements

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/entitlements/{account_id}` | Ownership state for one account |

**Response** (`EntitlementState`):
```json
{
  "accountId": "user_001",
  "ownsEveryVST": true,
  "ownedProducts": ["freeeq8", "therum"],
  "ownedBundles": ["maid_suite"],
  "extraSeatQuantity": 2,
  "billingState": "active"
}
```

### Seats

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/seats/{account_id}` | List all seat assignments for an account |

**Response** (`SeatAssignment[]`):
```json
[
  {
    "seatId": "seat_abc",
    "accountId": "user_001",
    "machineId": "mac-studio-01",
    "productId": "therum",
    "status": "active"
  }
]
```

### Runtime Validation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/validate-runtime` | Plugin launch-time auth check |

**Request** (`RuntimeValidationRequest`):
```json
{
  "accountId": "user_001",
  "machineId": "mac-studio-01",
  "productId": "therum",
  "edition": "pro",
  "runtimeVersion": "1.0.0"
}
```

**Response**: `{ "approved": true, "reason": "...", "features": [...], "seat": {...} }`

### Proposals

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/proposal` | Submit an install/update/upgrade proposal for ARC to decide |

**Request** (`ProposalRequest`):
```json
{
  "proposalId": "prop_001",
  "type": "install_missing",
  "accountId": "user_001",
  "machineId": "mac-studio-01",
  "requestedProducts": ["therum", "wurp"]
}
```

### GitHub Releases

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/releases/{product_id}` | Latest GitHub release for a product |
| `GET` | `/release-check` | Bulk latest-release check across all products |

### Stripe Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/stripe/webhook` | Receives Stripe webhook events |

Handled events:
- `checkout.session.completed` — new purchases
- `customer.subscription.created` / `updated` — seat changes
- `invoice.payment_failed` — billing issues

Requires the `STRIPE_WEBHOOK_SECRET` environment variable.

### Install Scan

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/install-scan` | Hub reports installed plugin state |

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full system design. The short version:

### ARC — Authority, Registry, Control
Canonical authority for product registry, entitlements, receipt ledger, seat registry, repo state, proposals, and authority decisions.

### Hub — Desktop Operator Surface
JUCE desktop app for browsing products, refreshing state, installing/updating, managing accounts, seats, and purchase flows.

### Plugins — Thin Clients
Each plugin identifies itself and calls `validate-runtime` through the plugin bridge. Plugins never make authorization decisions locally.

### Core Flows
1. **Refresh** — Hub scans local installs, fetches ARC catalog + entitlements + releases, computes card states.
2. **Install Missing** — Hub proposes → ARC validates ownership + release → Hub downloads.
3. **Pro Validation** — Plugin calls ARC → Complete Collection → bundle → product → free/open fallback → seat enforcement.
4. **Seat Allocation** — Ownership decides *what*, seat quantity decides *how many machines*.

### Data Layer
- **SQLite** with WAL mode and foreign keys for all user data (accounts, entitlements, seats, receipts).
- **Static JSON** for the product catalog (it's configuration, not user data).
- **JSON schemas** in `schemas/` for entitlement, product, and proposal validation.

## Project Structure

```
TizWildinEntertainmentHUB/
├── arc_service/
│   ├── app/
│   │   ├── main.py                 # FastAPI app + lifespan
│   │   ├── db.py                   # SQLite layer (WAL, FK, context manager)
│   │   ├── api/
│   │   │   └── routes.py           # All HTTP endpoints
│   │   ├── models/
│   │   │   └── domain.py           # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── catalog_service.py  # Product catalog loader
│   │   │   ├── entitlement_service.py
│   │   │   ├── seat_service.py
│   │   │   ├── proposal_service.py
│   │   │   ├── release_service.py  # GitHub Releases API polling
│   │   │   └── stripe_service.py   # Webhook signature + event dispatch
│   │   └── data/
│   │       └── products.catalog.json
│   ├── tests/                      # pytest suite (20 tests)
│   └── requirements.txt
├── hub_scaffold/                   # JUCE desktop app scaffold
├── plugin_bridge/                  # JUCE/C++ client module scaffold
├── manifests/
│   └── products.catalog.json       # Canonical product manifest
├── schemas/
│   ├── product.schema.json
│   ├── entitlement.schema.json
│   └── proposal.schema.json
├── stripe/                         # Stripe integration mapping
├── scripts/
│   └── migrate_mock_to_db.py       # Seeds SQLite from mock JSON
├── docs/
│   ├── ARCHITECTURE.md
│   ├── STATE_MODEL.md
│   └── STRIPE_NOTES.md
├── .github/
│   ├── workflows/ci.yml            # pytest + ruff on push/PR
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   └── FUNDING.yml
├── LICENSE                         # MIT
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
└── .gitattributes
```

## Testing

```bash
cd arc_service
pytest -v
```

**20 tests** covering:
- Catalog integrity (all products resolve, groups match, repo slugs present)
- Entitlement lookups (ownership, Complete Collection flag, missing accounts)
- Seat allocation (assign, list, deduplication, limit enforcement)
- Proposal decisions (install_missing, update, unknown types)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `STRIPE_WEBHOOK_SECRET` | For Stripe | Webhook signature verification secret |
| `GITHUB_TOKEN` | Optional | Raises GitHub API rate limit for release polling |

## Tech Stack

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI 0.115 |
| Data Validation | Pydantic 2.9 |
| Database | SQLite 3 (WAL mode) |
| HTTP Client | httpx 0.27 |
| Testing | pytest 8.3 |
| Server | Uvicorn |
| Desktop App | JUCE (scaffold) |
| Plugin Bridge | JUCE / C++ (scaffold) |
| Payments | Stripe Webhooks |
| Release Tracking | GitHub Releases API |

## Roadmap

### Shipped
- [x] Canonical product catalog with 13 products
- [x] Entitlement + seat management with SQLite persistence
- [x] Runtime validation endpoint
- [x] Proposal / authority decision system
- [x] GitHub release polling (per-product + bulk)
- [x] Stripe webhook handling (checkout, subscriptions, failed payments)
- [x] Receipt ledger
- [x] Test suite (20 tests)

### Next
- [ ] Production deployment (Docker + managed DB)
- [ ] Real installer actions (download + place binaries)
- [ ] JUCE Hub desktop app UI
- [ ] Plugin bridge runtime integration
- [ ] Stripe secret/backend deployment
- [ ] Automated release binary packaging
- [ ] Admin dashboard

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting bugs, suggesting features, and submitting pull requests.

## Security

See [SECURITY.md](SECURITY.md) for the vulnerability reporting process. **Do not open public issues for security vulnerabilities.**

## License

This project is licensed under the [MIT License](LICENSE).

---

Built by [GareBear99](https://github.com/GareBear99) · TizWildin Entertainment
