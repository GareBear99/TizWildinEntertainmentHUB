# TizWildin HUB API Documentation

**Base URL:** `https://tizwildin-hub.admension.workers.dev`

The HUB backend is a Cloudflare Worker handling authentication, licensing, subscriptions, and community features.

## Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/hub/community-stats` | GET | Community statistics |
| `/auth/google/signin` | POST | Google OAuth sign-in |
| `/auth/soundcloud/*` | POST/GET | SoundCloud OAuth |
| `/hub/signin` | POST | HUB account sign-in |
| `/hub/account` | GET | Full account status |
| `/activate` | POST | Activate ProEQ8 license |
| `/deactivate` | POST | Deactivate device |
| `/verify` | POST | Verify license |
| `/recover` | POST | Recover license via email |
| `/hub/master-key/status` | GET | Master Key status |
| `/hub/master-key/link` | POST | Link seat to email |
| `/hub/master-key/unlink` | POST | Unlink seat |
| `/hub/master-key/reset` | POST | Clear all seats |
| `/create-checkout` | POST | ProEQ8 checkout |
| `/create-checkout/master-key` | POST | Master Key checkout |
| `/webhook/stripe` | POST | Stripe webhooks |
| `/admin/subscribers` | GET | List all users |
| `/admin/send-weekly-newsletter` | POST | Trigger newsletter |

---

## Health & Status

### GET /health
```json
{ "status": "ok", "version": "1.0.0" }
```

### GET /hub/community-stats
```json
{
  "totalUsers": 42,
  "giveawayProgress": 4.2,
  "giveawayTarget": 1000
}
```

---

## Authentication

### POST /auth/google/signin
**Request:**
```json
{
  "email": "user@example.com",
  "name": "User Name",
  "googleId": "google-oauth-id"
}
```
**Response:**
```json
{
  "ok": true,
  "email": "user@example.com",
  "isNewUser": false,
  "loginCount": 5
}
```

### POST /hub/signin
**Request:**
```json
{
  "email": "user@example.com",
  "name": "User Name"
}
```

---

## ProEQ8 Licensing

### POST /activate
**Request:**
```json
{
  "email": "user@example.com",
  "licenseKey": "base64-encoded-license",
  "deviceId": "unique-device-identifier"
}
```
**Response:**
```json
{
  "ok": true,
  "activationId": "act_uuid",
  "product": "ProEQ8",
  "expiresAt": "2027-05-28T00:00:00.000Z"
}
```

### POST /deactivate
```json
{
  "email": "user@example.com",
  "deviceId": "unique-device-identifier"
}
```

### POST /verify
```json
{
  "email": "user@example.com",
  "licenseKey": "base64-encoded-license",
  "deviceId": "unique-device-identifier"
}
```

### POST /recover
```json
{ "email": "user@example.com" }
```

---

## Master Key Subscriptions

Master Key allows 1-3 seats per subscription at $3 CAD/seat/month.

### GET /hub/master-key/status?email={email}

**Owner Response:**
```json
{
  "hasMasterKey": true,
  "isOwner": true,
  "canManageSeats": true,
  "seats": 2,
  "seatsUsed": 1,
  "linkedEmails": ["teammate@example.com"],
  "licenses": { "teammate@example.com": "license-key" },
  "status": "active"
}
```

**Linked User Response:**
```json
{
  "hasMasterKey": true,
  "isOwner": false,
  "canManageSeats": false,
  "ownerEmail": "owner@example.com",
  "license": "your-license-key"
}
```

### POST /hub/master-key/link
**Request:**
```json
{
  "primaryEmail": "owner@example.com",
  "linkedEmail": "teammate@example.com"
}
```
**Response:**
```json
{
  "ok": true,
  "linkedEmail": "teammate@example.com",
  "license": "generated-license-key",
  "seatsUsed": 1,
  "seatsTotal": 2,
  "linkedEmails": ["teammate@example.com"]
}
```

### POST /hub/master-key/unlink
```json
{
  "primaryEmail": "owner@example.com",
  "linkedEmail": "teammate@example.com"
}
```

### POST /hub/master-key/reset
```json
{ "primaryEmail": "owner@example.com" }
```

---

## HUB Account

### GET /hub/account?email={email}
```json
{
  "email": "user@example.com",
  "hubAccount": {
    "name": "User Name",
    "provider": "google",
    "verified": true,
    "created": "2026-05-28T14:00:00.000Z"
  },
  "licenses": [{
    "product": "ProEQ8",
    "licenseKey": "key-here",
    "purchaseDate": "2026-05-28T14:00:00.000Z",
    "activations": 1,
    "maxActivations": 3
  }],
  "masterKey": {
    "isOwner": true,
    "canManageSeats": true,
    "seats": 2,
    "seatsUsed": 1,
    "linkedEmails": ["teammate@example.com"],
    "status": "active"
  }
}
```

---

## Stripe Checkout

### POST /create-checkout
ProEQ8 one-time purchase ($29.99 CAD).
```json
{
  "email": "user@example.com",
  "successUrl": "https://yoursite.com/success",
  "cancelUrl": "https://yoursite.com/cancel"
}
```

### POST /create-checkout/master-key
Master Key subscription (1-3 seats).
```json
{
  "email": "user@example.com",
  "seats": 2,
  "successUrl": "https://yoursite.com/success",
  "cancelUrl": "https://yoursite.com/cancel"
}
```

---

## Admin Endpoints

Requires `Authorization: Bearer {first-16-chars-of-RESEND_API_KEY}`

### GET /admin/subscribers
### POST /admin/send-weekly-newsletter

---

## Error Responses
```json
{ "error": "Error message" }
```

Status codes: `400` Bad Request, `401` Unauthorized, `403` Forbidden, `404` Not Found, `429` Rate Limited, `500` Server Error

## Rate Limiting
60 requests/minute per IP (except webhooks).

## CORS
Allowed origins: `https://garebear99.github.io`, `http://localhost:*`

---

## Environment Variables

**Required Cloudflare Worker Secrets:**
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_ID` (ProEQ8)
- `MASTER_KEY_PRICE_ID`
- `RESEND_API_KEY`
- `LICENSE_SIGNING_SECRET`

**Optional:**
- `SOUNDCLOUD_CLIENT_ID`
- `SOUNDCLOUD_CLIENT_SECRET`

## KV Namespace
ID: `86877ac372ca4fd694fb7b81092e857a`

Key patterns:
- `user:{email}` - Account data
- `license:{email}` - ProEQ8 license
- `activation:{email}:{deviceId}` - Device activations
- `master_key_sub:{email}` - Subscription metadata
- `master_key:{email}` - Seat assignments
- `mk_linked:{email}` - Reverse lookup for linked users

## Deployment
```bash
cd server
NODE_TLS_REJECT_UNAUTHORIZED=0 npx wrangler deploy
```

Cron: Weekly newsletter every Monday 10 AM UTC.
