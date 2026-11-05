# Cloudflare — workers, repos, and pings

Single inventory of every Cloudflare Worker in the TizWildin account, which
repo deploys it, and what pings it. Verified live 2026-11-05 (all health
endpoints probed; see "Pings tested" below). The workers.dev subdomain for
this account is **`admension`** — not `tizwildin`.

## Inventory

| Worker | Live URL | Live version | Health path | Repo / source | Repo version |
|---|---|---|---|---|---|
| tizwildin-hub | https://tizwildin-hub.admension.workers.dev | **3.1.0** | `/health` → 200 | `GareBear99/FreeEQ8` — `server/stripe-webhook.js`, `server/wrangler.toml` (name `tizwildin-hub`) | **3.2.0** (source is ahead of live; leak fix + 103 tests, uncommitted in FreeEQ8) |
| proeq8-license-server | https://proeq8-license-server.admension.workers.dev | **2.2.5** | `/health` → 200 | **UNKNOWN — no repo.** Old deployment name from the v2.2.0 era (`FreeEQ8/docs/RELEASE_v2.2.0.md`: "Deployed license worker …/proeq8-license-server…/health"). The worker was renamed to `tizwildin-hub` at v3.x; the old one was never deleted. | — |
| arc-ai-operator | https://arc-ai-operator.admension.workers.dev | **0.1.0** | `/` → 200 service card (there is **no** `/health` route — 404 is expected) | `GareBear99/gh-ai-operator` — `cloudflare/worker.js`, `cloudflare/wrangler.toml` (name `arc-ai-operator`) | 0.1.0 |
| rag-command-center-api | https://rag-command-center-api.admension.workers.dev | not reported (health has no version field) | `/api/health` → 200 (`/` and `/health` 404 — expected, no such routes) | `GareBear99/RAG-Command-Center` — `worker.js`, `wrangler.toml` (name `rag-command-center-api`) | HEAD `f7735e6a` |
| admension-api | https://admension-api.admension.workers.dev | not reported (health has no version field) | `/api/health` → 200 (`/health` 404 — health lives at `/api/health`) | `GareBear99/admension` — `worker.js`, `wrangler.toml` (name `admension-api`, KV `ADMENSION_LINKS`) | HEAD `a1f9010c` |
| (2 unnamed workers) | unknown | unknown | unknown | unknown | unknown — **BLOCKED.** The Cloudflare dashboard shows 7 workers; 5 are named above. The other 2 can only be identified from the dashboard or the Cloudflare API. The API token lives in Gary's Brave browser (Cloudflare dashboard, signed in as Gdoman99@gmail.com) — it is not in any Mac file. Fetch it from Brave when the Mac is free, then list the workers with `wrangler` / the API and fill in these two rows. |

## Who pings what

| Worker | Callers (what pings it) |
|---|---|
| tizwildin-hub | FreeEQ8 plugin (`FreeEQ8/Source/Config.h` — base URL `https://tizwildin-hub.admension.workers.dev`; `POST /activate`, `/verify`); HUB account page (`docs/pages/account.html` — `/hub/products`, `/hub/account`, `/hub/master-key/status`, `/create-checkout/product`, `/create-checkout/master-key`); `/health` checks. |
| proeq8-license-server | **NOTHING.** No live code points at it — not the plugin (uses tizwildin-hub), not the HUB pages, not the docs. The only references are historical (`FreeEQ8/docs/RELEASE_v2.2.0.md`) and the npm package name in `FreeEQ8/server/package.json`. It answers only health checks. |
| arc-ai-operator | Portfolio review page (`https://garebear99.github.io/Portfolio/review.html`); `POST /review` dispatches a code-review request to gh-ai-operator. |
| rag-command-center-api | RAG public site (`https://garebear99.github.io/RAG-Command-Center/` — `assets/js/public.js` calls `/api/inquiries`; `signals.html` calls `/api/compile`, `/api/signals`; `index.html` inquiry form POSTs `/api/inquiries`); hourly cron trigger compiles public signals (`[triggers] crons = ["0 * * * *"]` in `wrangler.toml`). |
| admension-api | ADMENSION frontend (`https://garebear99.github.io/admension/`); link create/fetch/update (`/api/links`), view/event collection (`/api/events`). |

## Pings tested (2026-11-05, from the VM — all live)

| Ping | Result |
|---|---|
| `GET tizwildin-hub…/health` | 200 `{"status":"ok","version":"3.1.0"}` ✓ |
| `POST tizwildin-hub…/activate` (dummy key `DUMMY-KEY-DOES-NOT-EXIST-0000`) | 400 `{"error":"Invalid license key"}` ✓ — correct rejection, no side effect |
| `GET proeq8-license-server…/health` | 200 `{"status":"ok","version":"2.2.5"}` ✓ |
| `POST proeq8-license-server…/activate` (dummy key) | 401 `{"error":"Invalid license key"}` ✓ — correct rejection (401 vs the new worker's 400 is a version difference, both reject) |
| `GET arc-ai-operator…/` | 200 service card (`service: arc-ai-operator-worker`, `version: 0.1.0`, `operator_repo: GareBear99/gh-ai-operator`) ✓ |
| `GET arc-ai-operator…/health` | 404 `{"error":"no route for /health"}` — expected, not a failure |
| `GET rag-command-center-api…/api/health` | 200 `{"status":"ok","service":"rag-command-center-api","ts":…}` ✓ |
| `GET rag-command-center-api…/api/stats` | 200 `{"success":true,"stats":{"inquiries_total":0,"events_today":0,…}}` ✓ |
| `GET rag-command-center-api…/api/signals` | 200 `{"success":true,"total":44,"signals":[]}` ✓ |
| `GET rag-command-center-api…/api/compile` | 200 `{"success":true,"compiled":0,"sources":["reddit_victoriabc","reddit_canadahousing","victoria_opendata"],"signals":[]}` ✓ |
| `GET rag-command-center-api…/` and `/health` | 404 `{"error":"not_found"}` — expected, no such routes |
| `GET admension-api…/api/health` | 200 `{"status":"ok","timestamp":…}` ✓ |
| `GET admension-api…/api/links/zzz-no-such-code-000` | 400 `{"error":"Invalid code format"}` ✓ — routing + validation work (not a 500) |
| `GET admension-api…/health` | 404 `{"error":"Not found"}` — expected, health lives at `/api/health` |
| `GET proeq8-checkout.tizwildin.workers.dev/` | **NXDOMAIN — dead, no worker** ✗ |
| `GET proeq8-checkout.admension.workers.dev/` | 404 `error code: 1042` — no worker deployed ✗ |

Notes: `POST /review` on arc-ai-operator was **not** probed live — it dispatches a real
GitHub review workflow, so a test call would have a side effect. `/hub/account`
was **not** re-probed here — the license-server work already confirmed it live
(unauthenticated `?email=` → HTTP 200, the leak; fixed in source v3.2.0, deploy
pending on the Cloudflare token).

## Mismatches found

1. **tizwildin-hub live 3.1.0 vs source 3.2.0.** The v3.2.0 source (FreeEQ8 repo,
   leak fix, 103/103 tests) is not deployed. Deploy is blocked on the Cloudflare
   API token (in Gary's Brave; fetch when the Mac is free). After deploy, verify
   `/health` reports `3.2.0` and unauthenticated `/hub/account` returns 401.
   The HUB account page is already ready for the fixed worker (commit `3f40da2` —
   it sends its session token on account reads).
2. **Two live license servers.** `tizwildin-hub` (3.1.0) and
   `proeq8-license-server` (2.2.5) both serve the license API. The second is the
   old v2.2.0-era deployment under the old name; it has no live callers. See
   "Ready to delete" below.
3. **Dead checkout subdomain.** `proeq8-checkout.tizwildin.workers.dev` is
   NXDOMAIN; nothing is deployed at `proeq8-checkout.admension.workers.dev`
   either. References live only in the FreeEQ8 repo (`server/pages/proeq8/
   checkout.js` + `success.html` set `WORKER_ORIGIN` to the dead subdomain;
   `docs/BACKEND_STATE.md`, `docs/CHECKOUT_DEPLOY.md` describe it). The HUB
   repo has no references to it. Fix belongs in the FreeEQ8 repo (not touched
   here — FreeEQ8 stays uncommitted until Gary says otherwise).
4. **`FreeEQ8/server/package.json` name is `proeq8-license-server`** while
   `wrangler.toml` deploys it as `tizwildin-hub`. Rename the package name to
   match the deployed worker (FreeEQ8 repo — report only, not changed here).
5. **Health endpoints are inconsistent.** tizwildin-hub + proeq8-license-server
   use `/health`; rag-command-center-api + admension-api use `/api/health`;
   arc-ai-operator has no health route at all (its `/` service card is the
   health surface). Each worker's canonical health path is in the table above.
   admension-api and rag-command-center-api report no version in their health
   responses, so the live version cannot be read from the endpoint.
6. **arc-ai-operator `POST /review` auth is unverified.** `WORKER_SHARED_SECRET`
   is optional in the worker code — if it is not set live, `/review` is open to
   anyone (it dispatches a GitHub workflow). Whether the secret is set cannot be
   checked without triggering a dispatch. Gary to confirm the secret is set, or
   set it (`wrangler secret put WORKER_SHARED_SECRET`).
7. **`/hub/master-key/link` + `/hub/master-key/unlink` are email-only** (same
   flaw as the `/hub/account` leak, not fixed in v3.2.0). Anyone knowing a Master
   Key owner's email can link/unlink seats. Needs a design decision + the account
   page sending proof on link/unlink.

## Ready to delete — awaiting Gary's confirmation (NOT deleted)

1. **`proeq8-license-server` worker (v2.2.5)** — delete AFTER `tizwildin-hub`
   v3.2.0 is deployed and verified live. Evidence: no live callers (plugin and
   HUB both use tizwildin-hub); it is the old v2.2.0-era deployment under the
   old name; its `/health` and `/activate` behave identically to the canonical
   worker (same code family, older version). Deleting it removes the second
   live license server.
2. Nothing else is deletable yet. The 2 unnamed workers are unidentified —
   they may be live and used, or dead. Do not delete anything until the
   dashboard/API listing names them.

## What is still blocked

- **The 2 unnamed workers** — need the Cloudflare dashboard or API. The API
  token lives in Gary's Brave browser (Cloudflare dashboard, signed in as
  Gdoman99@gmail.com). It is not in any Mac file (searched thoroughly). Fetch
  it from Brave when the Mac is free, then run `wrangler` / the API to list all
  7 workers and fill in the two missing rows above.
- **The tizwildin-hub v3.2.0 deploy** — same token blocker (separate work, deploy
  command ready: `cd FreeEQ8/server && CLOUDFLARE_API_TOKEN=<token> npx wrangler deploy`).
