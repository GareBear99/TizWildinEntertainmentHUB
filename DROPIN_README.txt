DROP-IN OVERLAY — TizWildinEntertainmentHUB itch indexing fix
================================================================
Extract this zip over the root of your repo checkout (it contains 256 files,
all relative to repo root), then:

  git rm --cached arc_service/app/data/arc_local_auth.sqlite3
  git add -A && git commit -m "fix: wire itch inventory into public index layer"

The one deletion (the committed sqlite auth DB) cannot be expressed in a zip
overlay, hence the git rm above. .gitignore now blocks it from returning;
sqlite_auth_service recreates the schema automatically (CREATE TABLE IF NOT
EXISTS) so nothing breaks.

WHAT'S IN HERE
- scripts/build_public_index.py ......... ingests all_items.json (67 products -> route pages,
                                          sitemap, llms.txt, JSON-LD, social cards), page_slug/
                                          render_page support, preserves source-* sitemap URLs,
                                          emits docs/ORPHAN_PAGES_REPORT.json
- scripts/update_itch_all_inventory.py .. bakes all-account-inventory.html (both copies) and
                                          ALL_ACCOUNT_INVENTORY.tsv on every run, --bake-only
                                          offline mode, fixed category rules, bundle kind,
                                          summary setdefault + correct counts
- scripts/validate_public_index.py ...... regression guards: itch coverage >= manifest count,
                                          inventory route in sitemap, seller-page snapshot
                                          freshness (both proven to trip)
- .github/workflows/itch-inventory-refresh.yml .. full chain: autopull -> build_public_index ->
                                          build_source_repo_index -> build_search_index ->
                                          build_index_health -> validators; truthful file_pattern
- index.html + docs/index.html .......... fixed all_items fallback fetch (data/all_items.json +
                                          resp.ok check)
- all_items.json + docs/data/all_items.json .. recategorized the 10 newly scraped items,
                                          bundle kind, summary counts corrected
- all-account-inventory.html + docs/pages/... .. rebaked: 67 items, 67 media-ready (was 57/0)
- ALL_ACCOUNT_INVENTORY.tsv ............. regenerated, 67 rows
- docs/* ................................ fully regenerated index layer: public-index.json
                                          (159 records incl. 68 itch), sitemap.xml (386 URLs),
                                          llms.txt, PUBLIC_LINK_GRAPH.md, ecosystem/arc index,
                                          67 itch route pages + social cards, search-index.json
                                          (6243 records), source-index refresh, index-health,
                                          ORPHAN_PAGES_REPORT.json
- .gitignore ............................ blocks *.sqlite3 under arc_service/app/data
- arc_service/app/main.py ............... version strings aligned (1.3.0)

VERIFIED BEFORE PACKAGING
- validate_public_index.py: OK (159 items, 386 sitemap URLs, 159 route pages)
- validate_source_index.py: OK (56 repos, 1000 files, 5028 links)
- all 20 scripts py_compile clean; SPA + seller-page JS parse clean (node --check)
- rebuild is now reproducible: rerunning the generator no longer drops itch
