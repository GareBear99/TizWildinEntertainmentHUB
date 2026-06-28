# All Itch Section Integration Notes

Generated: 2026-06-27

## What was added

- `all_items.json` — source-of-truth manifest for every public GareBearProductionz itch item visible before the supported/collection section.
- `docs/data/all_items.json` — static docs copy.
- `ALL_ACCOUNT_INVENTORY.tsv` — spreadsheet-friendly audit list.
- `index.html` / `docs/index.html` — new `🛒 All Itch` tab with filters and sale strips.
- `docs/pages/all-account-inventory.html` — standalone crawler/buyer landing page.
- `all-account-inventory.html` — root standalone preview page.

## Counts

- Public profile items indexed: 57
- Free / NYP items: 29
- Paid items: 28
- Formula A1 / $5k sale membership in manifest: 28
- Live SVG FX sale membership in manifest: 18

## Checkout authority

The HUB is only the buyer index and explanation layer. All purchase buttons route to official itch pages:

- Formula A1 (STEAL Bundle): https://itch.io/s/188490/formula-a1-steal-bundle
- Live SVG FX Pipeline Pack: https://itch.io/s/191122/live-svg-fx-pipeline-pack
- Full account: https://garebearproductionz.itch.io/

## Recommended next improvement

Turn each product card into a small proof card with one image/GIF thumbnail from itch, plus a short export-proof line such as `Includes: HTML, PNG, GIF, JSON, ZIP` where applicable.

## Media + autopull hardening added

The All Itch section now uses a `media` object per item:

```json
"media": {
  "cover": "",
  "animated": "",
  "type": "auto|image|gif|fallback",
  "alt": "Item title",
  "source": "itch-profile|itch-detail|pending-autopull",
  "updatedAt": "ISO-8601 timestamp"
}
```

Rendering behavior:

- If `media.animated` exists, the card uses it first so GIF previews play directly in the grid.
- If only `media.cover` exists, the card shows the cover image.
- If itch media fails or has not been pulled yet, the card renders a deterministic fallback block instead of breaking layout.
- Images use `loading="lazy"`, `decoding="async"`, and `referrerpolicy="no-referrer"` to keep the page fast and safer.

Autopull behavior:

- `scripts/update_itch_all_inventory.py` refreshes the public GareBearProductionz itch profile, stops before the supported/collection section, detects item links, prices, sale memberships, cover images, GIFs, and detail-page `og:image` media.
- The script writes both `all_items.json` and `docs/data/all_items.json` so the HUB can load the latest inventory exactly like the other no-cache manifests.
- `.github/workflows/itch-inventory-refresh.yml` can run manually or daily to keep the inventory fresh and commit changed JSON/media metadata back to the repo.

Important browser note:

Static GitHub Pages should not attempt to scrape itch.io HTML directly from the visitor browser because CORS may block it. The stable architecture is build-time autopull → manifest JSON → no-cache browser fetch.
