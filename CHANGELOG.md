# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project aims to follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Repository community standards and governance files:
  - `CONTRIBUTING.md`
  - `CODE_OF_CONDUCT.md`
  - `SECURITY.md`
  - `CHANGELOG.md`
  - `LICENSE`
- GitHub repository meta config:
  - `.gitattributes`
  - `.github/FUNDING.yml`
  - `.github/pull_request_template.md`
  - issue templates (`bug_report.md`, `feature_request.md`, `config.yml`)
  - CI workflow (`.github/workflows/ci.yml`)
- Comprehensive README overhaul:
  - architecture overview
  - full endpoint map
  - product catalog and repo mapping
  - quick start, testing, env vars, roadmap

## [0.1.0] - 2026-03-12

### Added
- SQLite persistence layer:
  - accounts
  - owned products
  - owned bundles
  - seats
  - receipts
- GitHub release polling service for product updates.
- Stripe webhook handling for:
  - `checkout.session.completed`
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `invoice.payment_failed`
- API endpoints:
  - `GET /releases/{product_id}`
  - `GET /release-check`
  - `POST /stripe/webhook`
- Product catalog `repoSlug` mapping for release checks.
- Test suite with 20 tests across catalog, entitlements, seats, and proposals.
- DB migration helper script: `scripts/migrate_mock_to_db.py`.

### Changed
- Migrated entitlement and seat services from mock JSON to SQLite.
- Updated FastAPI app startup to lifespan initialization.
- Expanded Python dependency set (`httpx`, `pytest`).
