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

## 2026-11-08 (Sun) — final (closes the in-progress section above)

- **API routes work:** none today — no new routes researched or used, no poster changes.
- **Bluesky posts:** no post verified from run history. bluesky-post-daily-am 07:42 PST and bluesky-post-daily-pm 13:42 PST fired, but neither run's summary confirms a post. Runonce bluesky-post-cloudworks 07:42 PST FAILED (held — queue order would have posted draft 09 Arcanum II Part 2 instead of the required draft 13 Cloudworks, so nothing ran). Runonce bluesky-post-shadow-run-vfx 13:42 PST FAILED (Mac offline — draft 14 Shadow Run VFX not posted). Evening retry bluesky-post-evening-retry-2026-11-08 20:00 PST FAILED (Mac offline, last seen 18:43 PST; no post attempted, 13:42 slot status unverifiable). Latest Bluesky post remains Nov 7 13:49 PST (Arcanum II Part 1).
- **Threads posts:** `06-kings-gambit.json` — The King's Gambit ($2.25 CAD) — POSTED 06:42 PST, verified live. `07-cloudworks.json` — Cloudworks ($6.99 CAD) — POSTED 14:06 PST, verified live (posted immediately on Gary's "posts too now", not waiting for slots). Midday 12:42 PST run: held, nothing posted (6h interval). Evening 18:42 PST run: no post — `08-shadow-run-vfx.json` and `09-adevils-game.json` held by the 6h interval (only 4.6h since Cloudworks). Next due: `10-gui-pack.json` 06:42 PST Nov 9.
- **Nostr posts:** #8 King's Gambit posted ~11:58 PST, verified live. #9 Cloudworks posted 17:00 PST, verified live (4/7 relays accepted).
- **Paying assets promoted:** The King's Gambit ($2.25 CAD — Threads + Nostr), Cloudworks ($6.99 CAD — Threads + Nostr). A Devil's Game ($2.10 CAD) did not go out (held by spacing). Bluesky promoted nothing today.
- **Acquired today:** New FREE itch listing "Avatar Generator — 2.4 Billion Succubus Combinations" (https://garebearproductionz.itch.io/avatar-generator), first seen in itch-seo autopull 85d0fd7 (11:45 PST); inventory 112 → 113 items. No new paid price points today (autopull only refreshed lastSeen); no sales verified; no sales-audit work today. Code landed (not itch): Lucid Google Drive OAuth + segment voice mp3s pushed to GitHub master (b525729); Lucid text-spacing pass committed locally as bundle bb88d35, not yet pushed (Mac offline).
- **New routes used/found:** none today.


## 2026-11-09 (Mon) — final (closes the in-progress section above)

- **API routes work:** none today — no new routes researched or used, no poster changes.
- **Bluesky posts:** `09-arcanum-ii-part2.json` — Arcanum II Part 2 ($2.16 CAD) — POSTED 06:50 PST, verified live via public API: https://bsky.app/profile/tizwildin.bsky.social/post/3mzv6ewgauw2k. Daily AM 07:42 PST and PM 13:42 PST runs fired; neither run summary confirms a further post. Referral boss draft `08-muse-referral-boss.json`: outcome UNCONFIRMED — still in the Mac queue at ~14:08 PST, 13:42 run summary empty; do not claim it posted.
- **Threads posts:** `08-shadow-run-vfx.json` — Live Smog VFX & Shadow Run Map Layers ($1.37 CAD) — POSTED 06:43 PST, verified live: https://www.threads.com/@garebearproductionz/post/DfhksKqjhtp. Midday 12:42 PST run: no post (6h interval, ~2 min early). Evening 18:42 PST run: no post — referral draft `08d-muse-referral-boss.json` dry-run at 18:42:46 PST, then a SKIP sweep at 18:43:51 PST with no POSTED line; state.json unchanged (last post still 06:43 PST), draft still in queue; the run was still listed running at 20:42 PST, final outcome open. Next due: `09-adevils-game.json` 06:42 PST Nov 10.
- **Nostr posts:** #10 A Devil's Game ($2.10 CAD sale) POSTED ~06:51 PST, verified live. #11 Muse referral (boss video) POSTED ~11:44 PST, verified live — today's one referral note. #12 Cloudworks ($6.99 CAD) POSTED ~16:44 PST, verified live.
- **Hive posts:** Orc Bungalo ($2.75 CAD) POSTED 10:23 PST, verified live. King's Gambit ($2.25 CAD) POSTED 16:42 PST, verified live.
- **Paying assets promoted:** Arcanum II Part 2 (Bluesky, $2.16 CAD), Live Smog VFX & Shadow Run Map Layers (Threads, $1.37 CAD), A Devil's Game (Nostr, $2.10 CAD sale), Cloudworks (Nostr, $6.99 CAD), Orc Bungalo (Hive, $2.75 CAD), King's Gambit (Hive, $2.25 CAD).
- **Acquired today:** itch inventory 113 → 115 (autopull dbbe07d, 15:48 PST): two new FREE listings — Boss Backgrounds — Free Pack and Minds Eye — Free Pack — both live on itch; Subwoofer Crown Bass Pack renamed (was "(FREE)") with updated 25 MB zip. No price changes today (autopull only refreshed lastSeen). No sales verified; no sales-audit work today. Queue work landed: Hive drafts 11–18 written for Nov 14–17 (prices + covers verified, dry-run PASS); Nostr runonce crons extended through Nov 19 (Riftedge, Animated VFX UI, Enchanted Sprite VFX, Pyre Fire).
- **New routes used/found:** none today.
- **Revenue:** $0 new today (no sales verified).
- **Could not verify:** Bluesky referral post (13:42 PM run summary empty, Mac poster logs not accessible from this VM); Threads evening run's final outcome (still listed running at 20:42 PST; no post in state.json or poster.log).
