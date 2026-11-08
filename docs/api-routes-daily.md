# Bluesky + Threads — Daily API-Routes Log

Daily record of what I do with the Bluesky + Threads API routes, for Gary.
One entry per day, newest last. Each entry: date, which API routes were used, which posts
went out on Bluesky and Threads, which paying assets were promoted, the result, and any
new routes found or used.

Rules: no secrets in this file — no tokens, no passwords, no app passwords, no account
credentials. Post IDs are machine handles and are NOT recorded here; the draft file name,
the asset, the platform, and the result are enough. The full route reference is
`~/workspace/bluesky-threads-api-routes.md`. A mirror of this file lives in the HUB repo
at `docs/api-routes-daily.md` for promotional continuity (same content, no secrets).

---

## 2026-11-07 (Sat)

- **API routes work:** Researched and documented the FULL Bluesky + Threads API routes
  (`~/workspace/bluesky-threads-api-routes.md`). Bluesky: AT Protocol XRPC — session
  (`createSession`/`refreshSession`/`deleteSession`), repo writes (`createRecord`,
  `uploadBlob`, `putRecord`, `deleteRecord`, `applyWrites`), post record
  (`app.bsky.feed.post`, facets, embeds, replies), video (`app.bsky.video.*`), public
  AppView reads (no account needed). Threads: Meta Threads API on
  `graph.threads.net/v1.0` — OAuth, two-step container flow (`POST /{user-id}/threads`
  then `POST /{user-id}/threads_publish`), `reply_to_id` replies, carousels, reply
  management, insights, `threads_publishing_limit` quota. Also documented the
  `threads-cli` connector commands the posters use. No new routes used and no poster
  changes after that.
- **Bluesky posts:** `11-arcanum-i-part2.json` — Arcanum I Part 2 ($2.88 CAD) —
  POSTED 07:47 PST, verified live via the public API; plain link only, no link card
  (itch.io returned 429 on the card fetch). `08-arcanum-ii-part1.json` — Arcanum II
  Part 1 ($2.88 CAD) — POSTED 13:49 PST, verified live; it posted in place of the
  scheduled draft 12 because the poster takes the lowest-numbered approved due draft.
  `12-kings-gambit.json` — King's Gambit — NOT posted (queue order, then the 2/day cap
  was reached); next slot Sun Nov 8 07:42 PST. Cron runs: bluesky-post-daily-am 07:42
  PST and bluesky-post-daily-pm 13:42 PST fired; bluesky-post-kings-gambit 13:42 PST
  reported failed (draft 12 did not post).
- **Threads posts:** `04-arcanum-i-part1.json` — Arcanum I Part 1 ($1.78 CAD) —
  POSTED 06:49 PST, verified live (publish call timed out after 300s but the post had
  gone live; reconciled, no duplicate). `threads/llmbuilder-thread.json` parts 1–4 —
  LLMBuilder repo promo thread — POSTED 06:49–06:57 PST, verified live. Midday run
  12:42 PST: HELD, nothing posted (6h interval not yet clear). `05-arcanum-i-part2.json`
  — Arcanum I Part 2 ($2.88 CAD) — POSTED 18:43 PST, verified live (text, image, itch
  link match draft). Note: a concurrent run of the morning job ran poster.py live while
  the main run was posting the thread — no duplicates resulted, but a possible duplicate
  cron trigger to investigate. Also recorded here (no Nov 6 entry exists in this log):
  `03-arcanum-ii-part2.json` — Arcanum II Part 2 — POSTED 21:47 PST Nov 6.
- **Paying assets promoted:** Arcanum I Part 1 ($1.78), Arcanum I Part 2 ($2.88),
  Arcanum II Part 1 ($2.88). (The LLMBuilder thread promoted the repo, not a paid asset.)
- **Acquired today:** itch sales-audit apply pass COMPLETE — Brief C batches C1–C3
  applied today (C1: 11 short descriptions + 12 funnel lines; C2: 12 + 11; C3: 12 + 12),
  completing Brief C and the whole apply pass (85 short descriptions + 36 funnel lines
  total); every free listing now funnels to the arena collection (source: itch listing
  updates). itch-seo autopull (2 refreshes today): inventory still 112 items, no new
  listings; new price points first seen today — Orc Bungalo Mystic Meadow Arena Kit
  $2.75, Animated VFX UI Pack (80 assets) $3.75 (−50%). No sales verified today.
- **New routes used/found:** none today.
