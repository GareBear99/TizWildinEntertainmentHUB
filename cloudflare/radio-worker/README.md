# TizWildin 24/7 Radio — Cloudflare Worker (song-load layer)

> Status: **code only, not deployed.** Nothing here touches Cloudflare.
> No R2 bucket, no Stream input, no KV namespace, no Paid plan.
> Deploying needs Gary's approval — it spends money (see below).

## What this is

The Cloudflare half of Gary's radio architecture:

- **GitHub Pages** = host + portal (the HUB page).
- **This Worker** = the song-load layer: queue selection, now-playing +
  history state, and serving audio.
- **R2** (not yet created) = gate-passed audio files.
- **Stream Live** (not yet created) = the true-live HLS feed, if Gary
  picks the live shape.

The Worker is `tizwildin-radio`, version `0.1.0`. Planned public URL once
deployed: `https://tizwildin-radio.admension.workers.dev`
(`admension` is this account's workers.dev subdomain — see `CLOUDFLARE.md`).

## Endpoints

| Route | What it does |
|---|---|
| `GET /health` | `{ status, service, version, live }` — `live` is true only when a Stream Live URL is configured |
| `GET /now-playing` | Current track, or `{ status: "offline", nowPlaying: null }` |
| `GET /history?limit=50` | Recent plays, newest first (max 200) |
| `GET /queue` | Queue status — **same shape as `radio_service`'s `/app/data/queue.json`**, so the Pages player and ARC can consume either source unchanged |
| `GET /tracks` | Registered track metadata (no audio) |
| `GET /stream.m3u8` | 302 to the Stream Live HLS URL when configured; **503 `{ status: "planned" }` while it isn't — never fakes a live stream** |
| `GET /song/:id` | Audio bytes from R2 (Range supported); 503 `planned` while R2 is unbound; 404 for unknown tracks |
| `POST /admin/advance` | Advance to the next track (Bearer `RADIO_ADMIN_SECRET`) |
| `POST /admin/tracks` | Replace the track registry `{ playlist: [...], submissions: [...] }` (Bearer `RADIO_ADMIN_SECRET`) |

Track entry: `{ id, title, artist, source, r2Key, addedAt }`.
History entry: `{ file, title, source, played_at }` — same shape the radio
service writes to `/app/data/history.json`.

## Queue logic (ported from `radio_service/queue_manager.py`)

`src/queue.js` is pure logic with no Cloudflare APIs, so it is unit-tested
in plain Node:

1. **Submissions first**, FIFO, each played **once** (played ids are
   remembered in KV state — this mirrors the fix in `queue_manager.py`
   that stopped a submission file replaying forever).
2. Otherwise the **playlist in shuffled order**, no repeat until every
   track has played, then it reshuffles.
3. Empty queue → no track (`/admin/advance` answers `idle`).

State lives in KV under `queue_state`; now-playing under `now_playing`;
history under `history` (max 200); the track registry under `tracks`.

## What this Worker deliberately does NOT do

**Run FFmpeg.** A Worker cannot run FFmpeg, so the quality gate does not
live here. The gate stays where it can run — in `arc_service`
(vendored copy at `arc_service/app/services/radio_quality_gate.py`) —
and only gate-passed tracks are registered in this Worker. Open question
(1) in the dissection: if the gate ever needs to move, the candidates are
Cloudflare Media Transformations or keeping it in arc_service.

## Local development & tests (no Cloudflare account needed)

```bash
cd cloudflare/radio-worker
npm test                    # node --test: 13 tests (queue logic + endpoints with KV/R2 stubs)
npx wrangler dev --local --port 8788 --persist-to /tmp/radio-worker-wrangler
curl localhost:8788/health         # {"status":"ok","service":"tizwildin-radio","version":"0.1.0","live":false}
curl localhost:8788/now-playing    # {"status":"offline","nowPlaying":null,"live":false}
curl localhost:8788/stream.m3u8    # 503 planned — honest, not a fake stream
```

Verified 2026-11-07: 13/13 unit tests pass; the Worker loads and answers
under `wrangler dev --local` (wrangler 4.158.0) with the placeholder KV id.
`--persist-to` points outside the repo so local dev state never lands in git.

## What Gary needs to enable (deploy checklist — Gary's call, in order)

1. **Workers Paid plan ($5/mo)** — required for Stream Live (Cloudflare
   docs: live streaming needs a paid Stream subscription or an eligible
   Pro/Business plan with Stream enabled). Workers Paid itself is $5/mo
   minimum and includes 10M requests + 30M CPU-ms/mo, then $0.30/M
   requests and $0.02/M CPU-ms. Free stays 100,000 requests/day, 10 ms
   CPU/invocation. Rates re-checked against Cloudflare's published
   pricing via secondary sources 2026-11-07 — **re-verify on Cloudflare's
   own pricing page before paying.**
2. **KV namespace** — `npx wrangler kv namespace create RADIO_KV`, paste
   the real id into `wrangler.toml` (the placeholder `0000…` is refused
   by `wrangler deploy` on purpose).
3. **R2 bucket `tizwildin-radio-audio`** — `npx wrangler r2 bucket create
   tizwildin-radio-audio`, then uncomment the `[[r2_buckets]]` block in
   `wrangler.toml`. R2 list pricing is ~$0.015/GB/mo storage with free
   egress (free tier includes 10 GB) — verify before committing.
4. **Upload gate-passed audio + register it** — upload mp3s to R2, then
   `POST /admin/tracks` with `{ id, title, artist, source, r2Key }`.
   Only tracks that passed the arc_service quality gate go in.
5. **Admin secret** — `npx wrangler secret put RADIO_ADMIN_SECRET`
   (never in the repo, never in a file).
6. **Deploy** — `npx wrangler deploy` (from this directory).
7. **Stream Live input (only if Gary picks the live shape)** — create a
   live input in the Cloudflare dashboard, set its HLS playback URL as
   the `STREAM_LIVE_URL` var in `wrangler.toml`, redeploy. Then
   `GET /stream.m3u8` 302s to the live feed and `/health` reports
   `live: true`.

## Cost warning — read before picking live-vs-loop

Stream bills **per viewer-minute delivered: $1 per 1,000 minutes
delivered, $5 per 1,000 minutes of recorded video stored** (ingest and
encoding free; list pricing, re-checked 2026-11-07 — verify on
Cloudflare's Stream pricing page before committing). A 24/7 stream
multiplies fast:

| Avg concurrent viewers | Viewer-minutes / month | Delivery cost / month |
|---|---|---|
| 1 | 43,200 | ~$43 |
| 10 | 432,000 | ~$432 |
| 100 | 4,320,000 | ~$4,320 |

That is the cost of the **true-live shape (a)**. The **looping-playlist
shape (b)** serves on-demand audio from R2 (free egress) and has no
per-viewer-minute delivery bill — but it is not one shared live broadcast.
**Gary has not picked a shape yet. Do not deploy Stream Live until he does.**

## YouTube 24/7 turn-on checklist (assessment only — nothing started)

The radio service already streams **only to YouTube RTMP**
(`radio_service/stream.py`: FFmpeg → `rtmp://a.rtmp.youtube.com/live2/<key>`).
To turn it on:

- [ ] **Stream key (Gary-only)** — from YouTube Studio → Go Live →
      Stream Key. Goes in `YOUTUBE_RTMP_KEY` via Secure Vault / env.
      **Never in the repo.** `stream.py` exits fatal if it is unset.
- [ ] **Music** — `radio_service/music/` is empty (only a 0-byte
      `.gitkeep`). Bootstrap from `SOUNDCLOUD_PLAYLIST_URL`
      (default `https://soundcloud.com/tizwildin/sets`) or drop mp3s in
      the directory. Without tracks the streamer waits in a loop.
- [ ] **Channel handle — Gary's call.** Every HUB surface uses
      **@gfgfvmhj** (`youtube.com/@gfgfvmhj`). `@TizWildin` appears in
      the awesome-python-audio-science list (outside this workspace,
      unverified). `@garebearproductionz` appears in
      `docs/LINK_CHECK_REPORT.json` (unverified). Do not assume — Gary
      confirms which channel the stream goes to.
- [ ] **Fan-out decision (open)** — dual-output FFmpeg (one encode,
      two RTMP outputs: Stream Live + YouTube) vs Stream Live onward to
      YouTube (Stream simulcast, reported $0.02/min/target — verify).
      Recorded as open; Gary decides. Note: simulcast is **not**
      available on WHIP inputs, only RTMPS/SRT — relevant if the ingest
      path changes.
- [ ] **Live-vs-loop pick (open)** — see cost warning above.
- [ ] **"Host rebound receive" confirmation (open)** — the working
      reading is that GitHub Pages receives the listener's request and
      rebounds it to Cloudflare, which serves the audio. Gary to confirm
      that is what he meant; the Worker + Pages player are built to that
      reading (player fetches the Worker endpoints; audio comes from
      Cloudflare).
- [ ] **Run it** — `docker compose up radio` (needs the key + music).
      The service has no health endpoint and no deploy script; first run
      is a manual watch of the FFmpeg log.

## Open questions (do not silently resolve)

1. **Quality gate location** — Worker cannot run FFmpeg. Gate stays in
   arc_service; Worker only serves gate-passed tracks. (Media
   Transformations is the unexamined alternative.)
2. **Live vs loop** — Gary's call (see cost warning).
3. **YouTube fan-out** — dual-output FFmpeg vs Stream onward (simulcast).
4. **"Host rebound receive"** — Gary to confirm the reading.
5. **Channel handle** — @gfgfvmhj vs @TizWildin vs @garebearproductionz.
