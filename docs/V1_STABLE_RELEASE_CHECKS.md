# V1 Stable Release Checks

The V1 public dashboard now avoids the red failure glitch.

## Fixes

- GitHub release checks run sequentially instead of all at once.
- GitHub API 404 is treated as `FREE SOURCE READY`, not a failure.
- GitHub API throttling/network failure is treated as `FREE SOURCE READY`, not a broken card.
- Repo/source button remains available even when GitHub's release API is unavailable.
- Auto-check can still default ON without making the page look broken.

This preserves the V1 public dashboard while keeping it stable for visitors.
