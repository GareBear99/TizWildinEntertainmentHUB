# V1 Conflict Clean Audit

This pass patched every HTML/JS dashboard file, not only `docs/index.html`.

## Rules now enforced

- No visible red failure state in the public V1 dashboard.
- GitHub API/network failures fall back to `FREE SOURCE READY`.
- Repo/source buttons stay visible.
- Release checks run sequentially, not in one burst.
- Auto-check defaults ON for first-time visitors.

## Changed files

- `docs/index.html`
- `hub_app/Source/TizHubMainComponent.cpp`

## Remaining conflict strings

- `README.md` contains `FREE SOURCE READY`
- `docs/V1_STABLE_RELEASE_CHECKS.md` contains `FREE SOURCE READY`