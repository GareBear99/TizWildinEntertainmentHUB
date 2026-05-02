# Architecture

TizWildin Entertainment HUB has three layers.

## 1. Public discovery layer

- `README.md`
- `docs/index.html`
- `plugins.json`
- `packs.json`
- Release Vault / SoundCloud / YouTube / FreeEQ8 links

This layer is the SEO and trust surface.

## 2. Local app layer

- `hub_app/`
- `hub_scaffold/`
- `plugin_bridge/`

This layer represents the desktop hub, plugin bridge, and product launcher direction.

## 3. Local service layer

- `arc_service/`
- `manifests/`
- `schemas/`
- `scripts/`

This layer handles catalog, mock auth, entitlements, install plans, staged releases, receipts, backups, diagnostics, and future account/payment integration.

## Core doctrine

The HUB is a router first: every feature should route the user toward a clear next useful action without overclaiming what is live.
