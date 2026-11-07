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
  `threads-cli` connector commands the posters use.
- **Bluesky posts:** none verified out as of ~03:10 PST (Mac poster logs are not
  accessible from the VM). Due today: Arcanum I Part 2 (07:42 PST), King's Gambit
  (13:42 PST).
- **Threads posts:** `03-arcanum-ii-part2.json` — Arcanum II Part 2 (256 Pixel Runes) —
  POSTED. Posted 2026-11-07T05:47:15Z (21:47 PST Nov 6). Route: `threads-cli publish-post`.
  Due today: Arcanum I Part 1 urgent send (06:45 PST), daily slots 06:42 / 12:42 / 18:42 PST.
- **Paying assets promoted:** Arcanum II Part 2 (Threads).
- **New routes used/found:** none used today — research only. Routes the posters do not
  use yet (available for later, Gary's call): Bluesky image embeds, video upload,
  reply threads, quotes, `deleteRecord`; Threads carousels, reply control, insights
  read-back, quota checks.
