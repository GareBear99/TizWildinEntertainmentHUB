# Product Card State Model

## Primary state enum
- installed
- not_installed
- partially_installed
- update_available
- source_update_available
- build_required
- owned
- free_open
- payment_issue
- coming_soon
- archived
- experimental

## Inputs to state calculation
- local install scan
- runtime version report
- ARC repo state
- ARC entitlement state
- release artifacts availability

## Example resolution order
1. If product status is `coming_soon`, show coming soon.
2. If payment failed for required subscription, show payment issue.
3. If not installed and binary exists, show not installed.
4. If not installed and only source exists, show build required.
5. If installed and repo version newer with binary, show update available.
6. If installed and repo version newer source-only, show source update available.
