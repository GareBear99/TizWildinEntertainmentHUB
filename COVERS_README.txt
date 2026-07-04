COVERS DROP-IN — real itch covers, native resolution, zero-jank loading
=========================================================================
WHAT THIS DOES
1) REAL COVERS EVERYWHERE. og:image, twitter:image, and JSON-LD image on all
   67 itch route pages now use the product's actual itch CDN cover/GIF instead
   of the generated SVG card (SVG stays as fallback for coverless items).
   Every route page also gets an on-page media hero.

2) NATIVE ITCH RESOLUTION. The scraper had harvested 32x32 thumbnail variants.
   All stored media URLs are normalized to the /original/ CDN variant — the
   SAME convention itch itself uses for its own og:image (verified live against
   your Doom raycaster listing). Resolution now matches the itch display
   exactly. The scraper is fixed at the source too (order-agnostic og:image
   regex + normalization), so tomorrow's autopull harvests full-res covers
   natively.

3) TRIPLE-BUFFERED ATOMIC SWAP, ZERO LAG. On route pages, the SPA itch tab,
   and the seller page:
     buffer A — CSS gradient placeholder (always painted; aspect-ratio box
                reserves layout, so cumulative layout shift = 0)
     buffer B — static cover shipped in the HTML (instant paint; crawlers and
                no-JS readers see it with no script)
     buffer C — the GIF, fetched and FULLY DECODED OFF-DOM via Image.decode(),
                then swapped in with one atomic src assignment — no progressive
                paint, no tearing, no reflow.
   Plus a CDN step-down: if /original/ ever 404s, the img retries the
   /315x250#c/ cover variant once before falling back to the branded card.

APPLY (from repo root):
  unzip -o ~/Downloads/TizWildin-COVERS-dropin.zip -d .
  rm -f COVERS_README.txt
  git add -A
  git commit -m "feat: native-res itch covers with triple-buffered atomic media swap"
  git push origin main

VERIFIED BEFORE PACKAGING
- 67/67 itch route pages: og:image + JSON-LD image on /original/ itch CDN URLs
- seller page baked manifest: 0 thumbnail URLs remaining, 112 /original/ refs
- validators: OK (159 items, 386 sitemap URLs, 159 route pages)
- SPA + seller page JS parse clean (node --check); generator compiles
- 67 itch route pages included in this zip
