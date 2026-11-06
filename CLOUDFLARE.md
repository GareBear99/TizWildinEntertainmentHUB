# Cloudflare — workers, repos, and pings

Single inventory of every Cloudflare Worker in the TizWildin account, which
repo deploys it, and what pings it. Account: Gdoman99@gmail.com, Account ID
`0848b8544de083a1587141a1e8aa3025`. The workers.dev subdomain for this account
is **`admension`** — not `tizwildin`.

Last full audit: **2026-11-05 ~18:08–19:20 PST** (read-only, in Gary's Brave;
source: `~/workspace/cloudflare-audit-2026-11-05.md`). Live versions below
were re-verified from the VM on 2026-11-05 ~20:24 PST.

## Inventory

| Worker | Live URL | Live version | Health path | Repo / source | Repo version |
|---|---|---|---|---|---|
| tizwildin-hub | https://tizwildin-hub.admension.workers.dev | **3.2.0** (deployed 2026-11-05 ~17:10 PST) | `/health` → 200 | `GareBear99/FreeEQ8` — `server/stripe-webhook.js`, `server/wrangler.toml` (name `tizwildin-hub`) | 3.2.0 — live and source now agree |
| arc-ai-operator | https://arc-ai-operator.admension.workers.dev | **0.1.0** | `/` → 200 service card (there is **no** `/health` route — 404 is expected) | `GareBear99/gh-ai-operator` — `cloudflare/worker.js`, `cloudflare/wrangler.toml` (name `arc-ai-operator`) | 0.1.0 |
| rag-command-center-api | https://rag-command-center-api.admension.workers.dev | not reported (health has no version field) | `/api/health` → 200 (`/` and `/health` 404 — expected, no such routes) | `GareBear99/RAG-Command-Center` — `worker.js`, `wrangler.toml` (name `rag-command-center-api`) | HEAD `f7735e6a` |
| admension-api | https://admension-api.admension.workers.dev | not reported (health has no version field) | `/api/health` → 200 (`/health` 404 — health lives at `/api/health`) | `GareBear99/admension` — `worker.js`, `wrangler.toml` (name `admension-api`, KV `ADMENSION_LINKS`) | HEAD `a1f9010c` |
| botfortress | https://botfortress.admension.workers.dev | `9c14bb1c` (deployed 9 months ago) | unknown — dormant, 1 invocation/day | Unknown repo — Assets binding only; no live callers found | — |
| botfortress-api | https://botfortress-api.admension.workers.dev | `3fdc9f13` (deployed 9 months ago) | `/` → 404 (no root route) | Unknown repo — Durable Object `BOT_QUOTA` + D1 `botfortress` bindings | — |

No unnamed workers remain — the two previously unidentified workers are
`botfortress` and `botfortress-api` (identified in the 2026-11-05 audit).

### Deleted

| Worker | Deleted | Notes |
|---|---|---|
| proeq8-license-server | 2026-11-05 ~17:35 PST (verified gone; `/health` now 404) | Old v2.2.5-era license server. Held Stripe secrets (`LICENSE_SIGNING_SECRET`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `MASTER_KEY_PRICE_ID`, `RESEND_API_KEY`, …) — all deleted with the worker. Its KV namespace name survives (see Storage). No live callers pointed at it. |

### Pages projects

| Project | URL | State |
|---|---|---|
| botfortress-web | `botfortress-web.pages.dev` | **No production deployment.** One preview deployment only, branch master, 2026-01-23, preview `ecdad412.botfortress-web.pages.dev`. No Git connection. |
| botfortress | `botfortress.pages.dev` | **Zero deployments ever** — "Create your first deployment" empty state. No Git connection. |

## Who pings what

| Worker | Callers (what pings it) |
|---|---|
| tizwildin-hub | FreeEQ8 plugin (`FreeEQ8/Source/Config.h` — base URL `https://tizwildin-hub.admension.workers.dev`; `POST /activate`, `/verify`); HUB account page (`docs/pages/account.html` — `/hub/products`, `/hub/account`, `/hub/master-key/status`, `/create-checkout/product`, `/create-checkout/master-key`); `/health` checks. |
| arc-ai-operator | Portfolio review page (`https://garebear99.github.io/Portfolio/review.html`) — **404 as of 2026-11-05** (verified; the repo `GareBear99/Portfolio` still exists, but the review page is gone, so this worker currently has no known live caller); `POST /review` dispatches a code-review request to gh-ai-operator. |
| rag-command-center-api | RAG public site (`https://garebear99.github.io/RAG-Command-Center/` — `assets/js/public.js` calls `/api/inquiries`; `signals.html` calls `/api/compile`, `/api/signals`; `index.html` inquiry form POSTs `/api/inquiries`); hourly cron trigger compiles public signals (`[triggers] crons = ["0 * * * *"]` in `wrangler.toml`). |
| admension-api | ADMENSION frontend (`https://garebear99.github.io/admension/`) — **404 as of 2026-11-05** (verified; the repo `GareBear99/admension` still exists, but its Pages site is gone, so this worker currently has no known live caller); link create/fetch/update (`/api/links`), view/event collection (`/api/events`). |
| botfortress | Nothing known — 1 invocation/day, dormant. |
| botfortress-api | Nothing known — 1 invocation/day, dormant. |

## Storage & databases

- **KV — 3 namespaces, 25 kB total stored** (Nov 6: Read 26, Write 17, Delete 0, List 0).
  - `admension-api-ADMENSION_LINKS` — `cad2d001ea9a42009b58cc57c9911f35` (bound to admension-api).
  - `proeq8-license-server-LICENSES` — `86877ac372ca4fd694fb7b81092e857a` — **misnamed: this namespace holds tizwildin-hub's live license data** (confirmed the same ID as the hub's `LICENSES` binding). It is live, just still named after the deleted proeq8-license-server worker. Renaming means re-binding the worker — see Decisions owed.
  - `rag-command-center-api-RAG_DATA` — `00eb93c98d32a480afb92b8214fa1fb3` (bound to rag-command-center-api).
- **D1 — 1 database:** `botfortress` (UUID `b0ba2ed6-596c-430d…`, truncated on screen), 0 tables, 1 query ever, 53.25 kB, created Jan 23 2026. Bound to botfortress-api. Effectively empty.
- **Durable Objects — 1 namespace, idle:** `BotQuotaTracker` (SQLite-backed), bound to botfortress-api. All usage zero (requests 0, errors 0, storage 0 B).
- **R2 — none.** Not subscribed, zero buckets. **Queues — zero. Workflows — zero.**
- **AI:** no AI Gateway, no Workers AI bindings, no Vectorize indexes. Never used.
- **Email:** Email Routing not enabled; Email Sending gated behind the Workers Paid plan. No domains onboarded.
- **Images & Stream, Realtime:** never used (0 images, 0 videos, no RealtimeKit apps).
- **Domains / DNS / zones — zero.** No domains registered with Cloudflare, no zones.

## Plan, billing, members

- **Plan: Workers Free** — the only subscription, Active. Free limits: 100,000 requests/day, 10 ms CPU/request. Paid is $5/mo + usage (10M requests/mo included, then $0.30/million; up to 5 min CPU/request; Containers & Email sending included).
- **Billing:** no payment method on file, no invoices. Billable usage (Beta): Argo traffic 0 B this month.
- **Members:** 1 member — gdoman99@gmail.com, Super admin, Status Active. **2FA appears NOT enabled** — see Decisions owed.
- **API tokens:** 1 user token total — "tizwildin-hub wrangler deploy" (Edit Cloudflare Workers template, scoped to this account, no expiration), created 2026-11-05 and last used ~17:10 PST the same day for the v3.2.0 deploy. Account API tokens: zero. Never record a token value anywhere.
- **Usage (last 24h, account home, 2026-11-05 audit):** total requests 114 (up 90%), worker invocations 94 (up 135%). Per-worker last 24h: tizwildin-hub 70→71 requests, 2.1 ms avg CPU, 0 errors; arc-ai-operator 5 invocations; rag-command-center-api 13; admension-api 8; botfortress 1; botfortress-api 1.
- **Other:** no OAuth clients, no blocked content, no abuse reports (no abuse report contact email is set), Workers for Platforms not set up, Containers not enabled, no tagged resources. Cloudflare Support edit access NOT granted (good).

## Audit logs (last 7 days, excluding "view" actions — 2026-11-05 audit)

8 actions, 1 unique actor (gdoman99@gmail.com), 1 product impacted, 0% failure — all 2026-11-05 (Mac times = PST+1h):

| Time (Mac) | Action | Object | Via |
|---|---|---|---|
| 18:35:02 | delete — Delete Worker | workers/scripts | Dashboard (proeq8-license-server deletion, ~17:35 PST) |
| 18:10:51 | update — Update Worker Script Schedules (Cron Triggers) | workers/scripts.schedules | API token |
| 18:10:51 | create — Update Worker Script Subdomain | workers/scripts.subdomain | API token |
| 18:10:50 | update — Patch Worker Script Settings | workers/scripts.script-settings | API token |
| 18:10:50 | create — Create Worker Deployment | workers/scripts.deployments | API token |
| 18:10:49 | create — Upload Version | workers/scripts.versions | API token |
| 18:09:23 | create — Create Token | user/tokens | Dashboard |

(The 8th action is the same set counted once more in the dashboard total; the 7 distinct rows above are what was shown. No other actor, no failures, nothing outside Nov 5.)

## Pings tested (2026-11-05, from the VM)

| Ping | Result |
|---|---|
| `GET tizwildin-hub…/health` | 200 `{"status":"ok","version":"3.2.0"}` ✓ — re-verified 2026-11-05 ~20:24 PST |
| `POST tizwildin-hub…/activate` (dummy key `DUMMY-KEY-DOES-NOT-EXIST-0000`) | 400 `{"error":"Invalid license key"}` ✓ — correct rejection, no side effect |
| Unauthenticated `GET tizwildin-hub…/hub/account?email=nobody@example.invalid` | 401 `{"error":"Unauthorized — sign in or provide a license key"}` ✓ — the account-read leak is fixed live (v3.2.0); re-verified 2026-11-05 ~20:24 PST |
| `GET proeq8-license-server…/health` | **404 — worker deleted 2026-11-05 ~17:35 PST** (was 200 `{"status":"ok","version":"2.2.5"}` before deletion) |
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
| `GET botfortress-api…/` | 404 — no root route; worker is dormant (1 invocation/day) |
| `GET proeq8-checkout.tizwildin.workers.dev/` | **NXDOMAIN — dead, no worker** ✗ |
| `GET proeq8-checkout.admension.workers.dev/` | 404 `error code: 1042` — no worker deployed ✗ |

Notes: `POST /review` on arc-ai-operator was **not** probed live — it dispatches a real
GitHub review workflow, so a test call would have a side effect.

## Mismatches found

1. **tizwildin-hub live 3.2.0 vs source 3.2.0 — RESOLVED 2026-11-05 ~17:10 PST.** The v3.2.0 deploy happened (API token created 18:09 Mac time, deploy 18:10 Mac time); `/health` now reports `3.2.0` and unauthenticated `/hub/account` returns 401 (both re-verified from the VM ~20:24 PST). The HUB account page already sends its session token on account reads (commit `3f40da2`).
2. **Dead checkout subdomain.** `proeq8-checkout.tizwildin.workers.dev` is NXDOMAIN; nothing is deployed at `proeq8-checkout.admension.workers.dev` either. References live only in the FreeEQ8 repo (`server/pages/proeq8/checkout.js` + `success.html` set `WORKER_ORIGIN` to the dead subdomain; `docs/BACKEND_STATE.md`, `docs/CHECKOUT_DEPLOY.md` describe it). The HUB repo has no references to it. Fix belongs in the FreeEQ8 repo (not touched here — FreeEQ8 stays uncommitted until Gary says otherwise).
3. **`FreeEQ8/server/package.json` name is `proeq8-license-server`** while `wrangler.toml` deploys it as `tizwildin-hub`. Rename the package name to match the deployed worker (FreeEQ8 repo — report only, not changed here).
4. **Health endpoints are inconsistent.** tizwildin-hub uses `/health`; rag-command-center-api + admension-api use `/api/health`; arc-ai-operator has no health route at all (its `/` service card is the health surface). Each worker's canonical health path is in the table above. admension-api and rag-command-center-api report no version in their health responses, so the live version cannot be read from the endpoint.
5. **arc-ai-operator `POST /review` auth is unverified.** `WORKER_SHARED_SECRET` is optional in the worker code — if it is not set live, `/review` is open to anyone (it dispatches a GitHub workflow). Whether the secret is set cannot be checked without triggering a dispatch. Gary to confirm the secret is set, or set it (`wrangler secret put WORKER_SHARED_SECRET`).
6. **`/hub/master-key/link`, `/unlink`, and `/reset` are email-only** (same flaw as the `/hub/account` leak, not fixed in v3.2.0). Anyone knowing a Master Key owner's email can link/unlink/reset seats. Needs a design decision + the account page sending proof on link/unlink/reset. (Recorded as a security follow-up note in `docs/API.md` next to those three endpoints, with the exact decision Gary owes; the account page never calls them, so no page change was needed.)
7. **tizwildin-hub Workers Logs/Traces are Disabled** — the live license server has no observability. Consider enabling Logs (Gary's call).

## Decisions owed — awaiting Gary (NOT acted on)

1. **Delete the dead workers:** `botfortress` (1 invocation/day, 9 months old, Assets binding) and `botfortress-api` (1 invocation/day, 9 months old; its D1 database `botfortress` — 0 tables, 1 query ever — and Durable Object namespace `BotQuotaTracker` — all usage zero — go with it).
2. **Delete the dead Pages projects:** `botfortress` (zero deployments ever — nothing to lose) and `botfortress-web` (no production deployment, one 9-month-old preview only).
3. **Review before deleting (barely used, has data attached):** `arc-ai-operator` (5 invocations/day, 6 months old, no bindings — its only known caller, the Portfolio review page, **404s as of 2026-11-05**, so it has no known live caller left), `rag-command-center-api` (13 invocations/day, 7 months old, KV `rag-command-center-api-RAG_DATA` attached), `admension-api` (8 invocations/day, 8 months old, KV `admension-api-ADMENSION_LINKS` attached — its only known caller, the ADMENSION Pages frontend, **404s as of 2026-11-05**).
4. **Enable 2FA** on the sole super-admin account (gdoman99@gmail.com) — it appears NOT enabled.
5. **Close the API Tokens tab in Brave** — it still shows the new token's value (Gary's action; the tab was open at audit time).
6. **Rename the misnamed KV namespace** `proeq8-license-server-LICENSES` — it holds tizwildin-hub's live license data. Renaming means re-binding the worker; decide whether the cosmetic fix is worth the touch.
7. **No abuse report contact email set** — add one so Cloudflare can forward abuse notices.
8. **Enable Logs/Traces on tizwildin-hub** (see mismatch 7).
9. **`/hub/master-key` ownership proof** (see mismatch 6; exact decision recorded in `docs/API.md`).
10. **`POST /review` auth on arc-ai-operator** (see mismatch 5).

## What is still blocked / not verified

- **The User API tokens (My Profile) page was not opened** during the audit — dashboard tooling blocks it (clicks on the Cloudflare header User menu open Brave's own menu; coordinate clicks in the top-right open Brave's Leo AI panel). The 1-token conclusion rests on the audit log + the deploy batch record, not on the token list itself.
- **AI / Realtime / Images sub-pages not opened individually** (Models, MCP Portals, AI Search, Agent tracing, TURN Server, Serverless SFU, MoQ Relay, Transformations, Live inputs, Stream analytics, Plans) — nothing is bound to them, no indexes or agents exist. Protect & connect / Monetize / Delivery & performance are zone-dependent; with zero zones nothing can be configured there. Zero Trust was not opened individually.
