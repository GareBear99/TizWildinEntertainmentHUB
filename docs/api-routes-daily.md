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

## 2026-11-10 (Tue)

- **Nostr posts:** #13 King's Gambit ($2.25 CAD) — POSTED ~10:44 PST, verified live on relay.primal.net + relay.nostr.net (event 86bbf99b…, note https://nostr.band/note1s6alnx6cu7n30vjclyffszmj5ksyne03ygr89yglkvrc64p6zu3saaryxk, 2/7 relays; damus 503, nos.lol + nostr.mom + wellorder timeouts, nostr.band connection lost). Cover via nostr.build: https://image.nostr.build/f765f08a5e0cb612f351d6bbcfbe2431c80a9739876009cfd300137b7b657af0.gif. No referral code in this note. Key read transiently from the Mac, never saved.
- **Nostr posts:** #14 A Devil's Game ($2.10 CAD) — POSTED ~16:43 PST, verified live on relay.primal.net + relay.nostr.net (event f1be56ec…, note https://nostr.band/note17xl9dmymw09t9vwc8vx7nvtq8aq79az3z7dxtxrahr35093kq2fquts45u, 2/7 relays; damus 503, nos.lol + nostr.mom + wellorder timeouts, nostr.band connection lost). Cover via nostr.build: https://image.nostr.build/f5b6c66bcb92bd5a289a4ec42b96ffad76b4f3a12e6336c6914471c898f67afc.jpg. No referral code in this note. Key read transiently from the Mac, never saved.
- **Paying assets promoted:** King's Gambit (Nostr, $2.25 CAD), A Devil's Game (Nostr, $2.10 CAD).
- **Revenue:** $0 new today (no sales verified).

## 2026-11-10 (Tue) — final (closes the in-progress section above)

- **API routes work:** none today — no new routes researched or used, no poster changes.
- **Bluesky posts:** no post verified from run history. bluesky-post-daily-am 07:42 PST and bluesky-post-daily-pm 13:42 PST fired but both were gate-held (recurring job takes over Nov 12; runonce crons own Nov 6–11). Runonce bluesky-post-adevils-game-pm 07:42 PST FAILED — Mac offline (last seen 07:17 PST), poster script never ran, draft 15 A Devil's Game not posted. Referral draft `08-muse-referral-boss.json`: outcome UNCONFIRMED — Mac poster logs not accessible from this VM.
- **Threads posts:** `08d-muse-referral-boss.json` — Muse referral (siren boss + code 7LU3P6) — POSTED 01:02 PST, verified live (late post from the Nov 9 18:42 run). `09-adevils-game.json` — A Devil's Game ($2.10 CAD, was $4.20) — POSTED 12:47 PST, verified live. `10-pharaohs-sands.json` — Pharaoh's Sands ($4.20 CAD, was $8.40) — POSTED 18:48 PST, verified live. Morning 06:42 PST run: no post (all drafts SKIP/HOLD on the 6h interval). Next due: `11-wisp-pack.json` at the 06:42 run Nov 11.
- **Nostr posts:** #13 King's Gambit ($2.25 CAD) POSTED ~10:44 PST, verified live. #14 A Devil's Game ($2.10 CAD) POSTED ~16:43 PST, verified live.
- **Hive posts:** Cloudworks ($6.99 CAD) POSTED 10:42 PST, verified live. Pharaoh's Sands ($4.20 CAD) POSTED 16:42 PST, verified live. Muse referral draft prepared today (approved, image via images.hive.blog), due ~20:45 PST — not yet posted at log time.
- **Paying assets promoted:** A Devil's Game (Threads + Nostr, $2.10 CAD), Pharaoh's Sands (Threads + Hive, $4.20 CAD), King's Gambit (Nostr, $2.25 CAD), Cloudworks (Hive, $6.99 CAD).
- **Acquired today:** itch inventory 115 → 117 (autopull 1d02640, 13:20 PST) — two NEW paid listings, both published today: Pharaoh's Sands — Desert Sun Court Arena Kit, $4.20 (https://garebearproductionz.itch.io/pharaohs-sands-desert-sun-court-arena-kit, published 12:20 PST); Flags & Banners Collection — Vol 1, $2.49 (https://garebearproductionz.itch.io/flags-banners-collection-vol-1, published 12:24 PST). No price changes in the autopull (only lastSeen refreshes); no sales verified; no sales-audit work today. Queue work landed: Nostr runonce crons extended through Dec 4 (49 crons); Pharaoh's Sands swapped into the next slot on Nostr (Nov 11 10:42), Hive (posted 16:42) and Threads (posted 18:48); stale Dec 1 Nostr Pharaoh's Sands cron ($10.00) removed and replaced with Fireball Generator Formula ($7.50). Hive draft 61 (Dec 9, Pharaoh's Sands) still carries the stale $10.00 price — needs re-pricing to $4.20 when next touched.
- **New routes used/found:** none today.
- **Revenue:** $0 new today (no sales verified).
- **Could not verify:** Bluesky — no post verified from run history (Mac poster logs not accessible from this VM); referral draft 08 outcome unconfirmed; Pharaoh's Sands Bluesky queue swap outcome unconfirmed (coordinator's Bluesky result never landed).

## 2026-11-11 (Wed)

- **Nostr posts:** Elemental Wisp Sprite Pack ($2.16 CAD) — POSTED ~16:42 PST, verified live on relay.primal.net + relay.nostr.net (event 972e726f…, note https://nostr.band/note1juh8ymchexvvrrfystxnu45mrgdlrtyj3rexpg0wzv642a7q4wsswkxa9k, 3/7 relays accepted at post time: damus, primal, nostr.net; nos.lol + nostr.mom timeouts, wellorder 503, nostr.band connection lost). Cover via nostr.build: https://image.nostr.build/c8b0b5fbe3fa520cc55c44a5977684053f487f6647b190b6f3398585e453aed8.png. No referral code in this note. Key read transiently from the Mac, never saved. Verification note: nostr.band page itself would not load in the browser (whole domain timed out, retried) and damus returned 503 on the later relay re-query — event confirmed live by direct relay REQ on primal + nostr.net with exact content.
- **Paying assets promoted:** Elemental Wisp Sprite Pack (Nostr, $2.16 CAD).
- **Revenue:** $0 new today (no sales verified).

## 2026-11-11 (Wed) — final (closes the in-progress section above)

- **API routes work:** none today — no new routes researched or used, no poster changes.
- **Bluesky posts:** no post verified from run history. bluesky-post-daily-am 07:42 PST and bluesky-post-daily-pm 13:42 PST both fired (succeeded, empty summaries — no post confirmed). Mac poster logs not accessible from this VM. Referral draft `08-muse-referral-boss.json` outcome still unconfirmed.
- **Threads posts:** `11-wisp-pack.json` — Elemental Wisp Sprite Pack ($2.16 CAD) — POSTED 11:51 PST, verified in state.json + poster.log. Morning 06:42 PST run FAILED: six drafts timed out at 300s each (11-wisp-pack, 12-808-producer-kit, 13-animated-vfx-ui-pack, 14-necromancers-toolkit, 20-gui-pack, 200-impact-fx-advanced), no post; verified none of the timed-out attempts landed, so the 11:51 post came from an off-schedule retry — no named cron run in history covers it. Midday 12:42 PST run: no post (HOLD — 0.8h since the wisp post, 6h interval). Evening 18:42 PST run FAILED: due draft `12-808-producer-kit.json` (808 Producer Kit, $1.37 CAD) not posted — six drafts timed out at 300s each waiting on a fresh publish approval; one approval is pending and unanswered. A 19:55 PST poster sweep dry-ran 12-808-producer-kit only (no post). threads-referral-weekly 18:00 PST fired (succeeded, empty summary); no post verified. Next due: `12-808-producer-kit.json` at 06:42 PST Nov 12 — the pending publish approval must be granted first.
- **Nostr posts:** Elemental Wisp Sprite Pack ($2.16 CAD) — POSTED ~16:42 PST, verified live on relay.primal.net + relay.nostr.net (event 972e726f…, note https://nostr.band/note1juh8ymchexvvrrfystxnu45mrgdlrtyj3rexpg0wzv642a7q4wsswkxa9k, 3/7 relays accepted at post time: damus, primal, nostr.net; nos.lol + nostr.mom timeouts, wellorder 503, nostr.band connection lost). Cover via nostr.build: https://image.nostr.build/c8b0b5fbe3fa520cc55c44a5977684053f487f6647b190b6f3398585e453aed8.png. No referral code in this note. Key read transiently from the Mac, never saved. Verification note: nostr.band page itself would not load in the browser (whole domain timed out, retried) and damus returned 503 on the later relay re-query — event confirmed live by direct relay REQ on primal + nostr.net with exact content.
- **Hive posts:** Muse referral (wake-up-1-billion-muse-tokens-is-not-a-typo) POSTED 04:51 PST, verified live: https://hive.blog/@tizwildin/wake-up-1-billion-muse-tokens-is-not-a-typo. Morning 10:42 PST run FAILED and afternoon 16:42 PST run FAILED — both on insufficient RC mana (AM: tizwildin 309,870,483 RC vs ~1,231,484,342 needed; PM: 550,338,050 RC vs ~1,250,759,753 needed); draft `05-arcanum-i-part-2.json` not posted, stays approved in queue. RC affordable again ~09:41 PST Nov 12.
- **Paying assets promoted:** Elemental Wisp Sprite Pack (Threads + Nostr, $2.16 CAD).
- **Acquired today:** itch inventory 117 → 119 (autopull 4488220, 14:00 PST) — two NEW paid listings, both $2.22 CAD, first seen in this autopull: Pharaoh's Sands Crowds (https://garebearproductionz.itch.io/pharaohs-sands-crowds) and Arena Crowds Collection (https://garebearproductionz.itch.io/arena-crowds-collection). Price changes in the same autopull: Flags & Banners Collection — Vol 1 $2.49 → $1.66; Coin Physics Pack $11.24 → $7.49; Gossamer Pixel Cobwebs $1.12 → $0.75; Cloudworks $6.99 → $3.49. No sales verified; no sales-audit work today. Queue note: today's cuts leave several queued drafts stale — Hive draft 62 Flags & Banners ($3.33, now $1.66), Hive draft 22 Coin Physics ($11.24, now $7.49), Hive draft 21 Gossamer ($1.12, now $0.75), Nostr Nov 25 AM Coin Physics cron ($11.24), Nostr Nov 21 AM Gossamer cron ($1.12); Hive draft 61 Pharaoh's Sands still $10.00 (price unchanged at $4.20) — all need re-pricing when next touched.
- **New routes used/found:** none today.
- **Revenue:** $0 new today (no sales verified).
- **Could not verify:** Bluesky — no post verified from run history (Mac poster logs not accessible from this VM); referral draft 08 outcome unconfirmed; the exact mechanism of the 11:51 PST Threads wisp post (no named cron run in history covers it — the 06:42 run failed and the post landed off-schedule).

## 2026-11-12 (Thu)

- **Nostr posts:** Arcanum I — Part 1 ($1.78 CAD) — POSTED ~10:43 PST, verified live on relay.primal.net + relay.nostr.net (event cd675c4b…, note https://nostr.band/note1e4n4cj7f2nnnzyrwevz8dp4cmxtjhuaqy254kyal8sy2jyht4c9ss6frv3, 2/7 relays; damus 503, nos.lol + nostr.mom timeouts, nostr.band connection lost, wellorder 503). Cover via nostr.build: https://image.nostr.build/9950611870dc65e3d200c8995f0548ac2bc22e1f6f4434d5f949b44a8b3cc574.jpg. No referral code in this note. Key read transiently from the Mac, never saved.
- **Nostr posts:** Impact FX Advanced — 12 Hero Pixel VFX ($3.89 CAD) — POSTED ~16:43 PST, accepted by relay.primal.net + relay.nostr.net per the poster (2/7 relays; damus 503, nos.lol + nostr.mom + wellorder timeouts, nostr.band connection lost). Event f154496f…, note https://nostr.band/note1792yjmca53gde46sxu6lpjqc59hr65ua2nte32qc9w5m982ra25qn62wgc. Cover via nostr.build: https://image.nostr.build/630e78de5b856071e17d158bac3f83aaeffc0acbbeb8d534c74135b7672a51b0.jpg. No referral code in this note. Key read transiently from the Mac, never saved. Verification caveat: independent live re-query could NOT be completed — direct relay REQ to primal/nostr.net timed out twice, damus still 503, nos.lol timed out, and nostr.band would not load at all in the browser (ERR_TIMED_OUT on repeated tries) — same flaky-relay pattern as recent runs; the note's live status rests on the two accepting relays' OK replies at post time.
- **Paying assets promoted:** Arcanum I — Part 1 (Nostr, $1.78 CAD), Impact FX Advanced (Nostr, $3.89 CAD).
- **Revenue:** $0 new today (no sales verified).

## 2026-11-12 (Thu) — final (closes the in-progress section above)

- **API routes work:** none today — no new routes researched or used, no poster changes. (The poster fail-stop fix — a failed publish now stops after 1 attempt instead of burning 6×300s — landed Nov 11 ~19:55 PST, not today.)
- **Bluesky posts:** `10-arcanum-i-part1.json` — Arcanum I — Part 1 ($1.78 CAD) — POSTED 07:38 PST, verified live: https://bsky.app/profile/tizwildin.bsky.social/post/3n24sh3vqa422 (poster took draft 10 in filename order, not draft 15 A Devil's Game). Weekly referral run 10:42 PST: HELD on the 6h cap (3.2h since last post), nothing posted. `01-muse-referral-wakeup.json` — Muse referral, code 7LU3P6 — POSTED 13:49:56 PST, verified live: https://bsky.app/profile/tizwildin.bsky.social/post/3n25h7id6m52v (muse.ai link card present). 2/2 posts today.
- **Threads posts:** `12-808-producer-kit.json` — 808 Producer Kit ($1.37 CAD) — POSTED ~07:34 PST, verified live: https://www.threads.com/@garebearproductionz/post/DfpY2CPCWaT. Morning 06:42 PST run FAILED: publish approval pending, poster timed out after 300s, verified no post had landed at that point — the post landed on a retry after the pending approval expired. Midday 12:42 PST run: no post (HOLD — 5.1h since last post, 6h interval). Evening 18:42 PST run FAILED: due draft `13-animated-vfx-ui-pack.json` (Animated VFX UI Pack, $3.75 CAD) not posted — publish approval pending and unanswered. Next due: `13-animated-vfx-ui-pack.json` at 06:42 PST Nov 13, pending that approval.
- **Nostr posts:** Arcanum I — Part 1 ($1.78 CAD) — POSTED ~10:43 PST, verified live on relay.primal.net + relay.nostr.net (event cd675c4b…, note https://nostr.band/note1e4n4cj7f2nnnzyrwevz8dp4cmxtjhuaqy254kyal8sy2jyht4c9ss6frv3, 2/7 relays). Impact FX Advanced — 12 Hero Pixel VFX ($3.89 CAD) — POSTED ~16:43 PST, accepted by relay.primal.net + relay.nostr.net per the poster (event f154496f…, note https://nostr.band/note1792yjmca53gde46sxu6lpjqc59hr65ua2nte32qc9w5m982ra25qn62wgc). No referral code in either note. Key read transiently from the Mac, never saved.
- **Hive posts:** Morning 10:42 PST run FAILED on RC mana short (tizwildin 1,272,141,642 RC vs 1,297,595,072 needed, shortfall 25,453,430); draft 05 Arcanum I Part 2 not posted, affordable again ~11:20 AM PST. Afternoon 16:42 PST run: `05-arcanum-i-part-2.json` — Arcanum I — Part 2 ($2.88 CAD) — POSTED, verified live: https://hive.blog/@tizwildin/arcanum-i-part-2-animated-pixel-spell-abilities-23-spells-752-frames.
- **Paying assets promoted:** Arcanum I — Part 1 (Bluesky + Nostr, $1.78 CAD), 808 Producer Kit (Threads, $1.37 CAD), Impact FX Advanced (Nostr, $3.89 CAD), Arcanum I — Part 2 (Hive, $2.88 CAD). (The Muse referral post is not a paid asset.)
- **Acquired today:** itch inventory unchanged at 119 — autopull b600ce9 (03:25 PST) only rebuilt the sitemap; no new listings, no price changes in all_items.json / price-history.json. No sales verified; no sales-audit work today. Code landed (not itch): Lucid feed-ordering (bd37f53) + ghost-words/widgets waves pushed (f7b0f90); ADMENSION pushed (f0b11a3); garebear99.github.io root site created + pushed (da6206f), Pages live; SlushAI Stage 1 curation completed (STAGE1.md). Clawbot always-on launchd stack unloaded (4 jobs disabled, plists moved aside, not deleted).
- **New routes used/found:** none today.
- **Revenue:** $0 new today (no sales verified).
- **Could not verify:** the exact mechanism of the 07:34 PST Threads 808 post (no named cron run covers it — the 06:42 run failed and the post landed on a retry after its pending approval expired); the Impact FX Advanced Nostr note's live status beyond the two accepting relays' OK replies (independent live re-query timed out on primal/nostr.net, damus 503, nostr.band would not load).

## 2026-11-13 (Fri) — final (closes the in-progress section above)

- **API routes work:** none today — no new routes researched or used, no poster changes. (The evening Threads run stopped after 1 failed publish attempt, per the fail-stop fix that landed Nov 11.)
- **Bluesky posts:** `15-adevils-game.json` — A Devil's Game — Hellfire Arena Kit ($2.10 CAD, was $4.20) — POSTED 07:51:51 PST, verified live via Bluesky public API: https://bsky.app/profile/tizwildin.bsky.social/post/3n27do3qa3p2s. Link card posted without thumbnail (image 2,017,923 bytes exceeds Bluesky's 1 MB limit). `12-kings-gambit.json` — THE KING'S GAMBIT — Gothic Arena Kit — POSTED 13:52 PST, verified live: https://bsky.app/profile/tizwildin.bsky.social/post/3n27xtajmag2v (link card present, thumb dropped, 1.87 MB). 2/2 posts today, at the 2/day cap. Next due draft: 13-cloudworks at 07:42 PST Nov 14.
- **Threads posts:** `13-animated-vfx-ui-pack.json` — Animated VFX UI Pack ($3.75 CAD) — POSTED 07:05:15 PST, verified live: https://www.threads.com/@garebearproductionz/post/Dfr6VQ6joaw. Note: the publish CLI timed out after 300s but the post had landed; reconciled in state.json and the draft moved to done/ to prevent a duplicate at the 12:42 run. Midday 12:42 PST run: no post (HOLD — 5.6h since last post, 6h interval). Evening 18:42 PST run FAILED: due draft `14-necromancers-toolkit.json` (NECROMANCER'S TOOLKIT — Expanded Ritual World Bundle, $12.00 CAD) not posted — publish CLI timed out after 300s; verified via profile-threads and state.json that it never landed. Draft remains approved+due for the next pass. No llmbuilder thread file (post-thread.log unchanged since Nov 7).
- **Nostr posts:** Shadow Run — Live Smog VFX & Map Layers ($1.37 CAD) — POSTED ~10:42 PST, verified live on relay.primal.net + relay.nostr.net (event 867ffb6c…, note https://nostr.band/note1sellkm973kdwtnd7hpxy0scca3ksg2ysx006v4thzrv4ktdqn6xsc8q2ge, 3/7 relays accepted at post time: damus, primal, nostr.net). Dark Fantasy Modular GUI Pack ($7.15 CAD) — POSTED ~16:42 PST, verified live on relay.primal.net + relay.nostr.net (event f779ce84…, note https://nostr.band/note17auuapycevzy3fpfwjv0zf8k0seydp4yaj3a5vka5vdvaetupqcquumn0v, 2/7 relays accepted at post time: primal, nostr.net). No referral code in either note. Key read transiently from the Mac, never saved.
- **Hive posts:** no post today — both runs failed on insufficient RC mana. Morning 10:42 PST: draft 06-impact-fx-advanced, tizwildin 940,241,398 RC vs 1,367,892,104 needed. Afternoon 16:42 PST: tizwildin 1,180,909,411 RC vs 1,385,586,058 needed. Draft remains unposted in queue.
- **Paying assets promoted:** A Devil's Game (Bluesky, $2.10 CAD), THE KING'S GAMBIT (Bluesky), Animated VFX UI Pack (Threads, $3.75 CAD), Shadow Run (Nostr, $1.37 CAD), Dark Fantasy Modular GUI Pack (Nostr, $7.15 CAD).
- **Acquired today:** itch inventory 119 → 121 (paid 70 → 72, free 49 unchanged) — two NEW paid listings first seen in today's autopulls: Palm Primal — Pygmy Tribes Arena Kit ($4.20 CAD, autopull 04f44cb, 13:27 PST; https://garebearproductionz.itch.io/palm-primal-pygmy-tribes-arena-kit) and Pharaoh's Sands Operators ($1.25 CAD, autopull 249ac01, 03:08 PST; https://garebearproductionz.itch.io/pharaohs-sands-operators). No price changes in all_items.json / price-history.json (only lastSeen bumps). No sales verified; no sales-audit work today.
- **New routes used/found:** none today.
- **Revenue:** $0 new today (no sales verified).
- **Could not verify:** the exact mechanism of the 07:05 PST Threads VFX UI Pack post (publish CLI timed out at 300s yet the post landed — same pattern as the Nov 12 808 post, which also landed on a retry after its approval expired); the Nostr GUI Pack note's live status beyond the two accepting relays' OK replies at post time (independent re-query confirmed it live on primal + nostr.net).
