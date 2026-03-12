# Architecture

## System split

### ARC
Canonical authority for:
- product registry
- entitlements
- receipt ledger
- seat registry
- repo state
- proposals
- authority decisions

### Hub
Desktop operator surface for:
- browsing products
- refresh
- install missing
- checking updates
- account state
- seat management
- opening purchase flows

### Plugins
Thin clients that:
- identify product/version/edition
- validate authority
- open the hub for manage/upgrade flows

## Core flows

### Refresh flow
1. Hub loads local registry.
2. Hub scans install paths.
3. Hub fetches ARC catalog + entitlement state.
4. Hub fetches repo state.
5. Hub computes visual card states.

### Install missing flow
1. Hub proposes `install_missing`.
2. ARC validates product ownership + release availability.
3. ARC returns authority decision.
4. Hub downloads binaries or marks build-required.

### Pro validation flow
1. Plugin bridge sends `validate_runtime_access`.
2. ARC resolves Complete Collection -> bundle -> product -> free/open.
3. ARC enforces seat availability.
4. ARC returns decision + features.

### Seat flow
- Product ownership decides what is allowed.
- Seat quantity decides how many machines may be active.
- Extra seats are billed through Stripe quantity-based subscription.
