# Architecture

## Rule
**Stripe bills. ARC decides. Hub operates. Plugins ask.**

## Components

### ARC
Authority service for:
- catalog truth
- entitlements
- seat assignment and release
- runtime validation
- install/update planning
- account summary aggregation
- webhook ingestion and mock entitlement mutation

### HUB
Desktop operator surface for:
- catalog browsing
- entitlement visibility
- install / update plans
- seat visibility and release
- billing handoff
- local scan reporting

### Plugin Bridge
Thin in-plugin client for:
- runtime validation
- hub handoff
- denial reason handling
