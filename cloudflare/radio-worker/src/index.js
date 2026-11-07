// TizWildin 24/7 Radio — Cloudflare Worker (song-load layer).
//
// What this is: the Cloudflare half of Gary's radio architecture.
// GitHub Pages is the host + portal; this Worker is the song-load layer:
// queue selection, now-playing + history state, and serving audio.
//
//   GET  /health          -> { status, version, live } (live = Stream URL configured)
//   GET  /now-playing     -> current track entry, or { nowPlaying: null, status: "offline" }
//   GET  /history?limit=  -> recent plays, newest first
//   GET  /queue           -> queue status (same shape as radio_service's queue.json)
//   GET  /tracks          -> registered track metadata (no audio)
//   GET  /stream.m3u8     -> 302 to the Stream Live HLS URL when configured,
//                            else 503 { status: "planned" } — never fakes live
//   GET  /song/:id        -> audio bytes from R2 when bound, else 503 planned
//   POST /admin/advance   -> advance to the next track (Bearer RADIO_ADMIN_SECRET)
//   POST /admin/tracks    -> replace the track registry (Bearer RADIO_ADMIN_SECRET)
//
// Bindings (see wrangler.toml):
//   RADIO_KV (KVNamespace) — now-playing, history, track registry, queue state.
//   RADIO_AUDIO (R2Bucket, optional until the bucket exists) — gate-passed audio.
// Vars:
//   STREAM_LIVE_URL — Cloudflare Stream Live HLS playback URL (empty until
//     a live input exists; /stream.m3u8 answers 503 while it is empty).
// Secrets (set with `wrangler secret put`, never in the repo):
//   RADIO_ADMIN_SECRET — Bearer token for the /admin/* routes.
//
// What this Worker deliberately does NOT do: run FFmpeg. A Worker cannot
// run FFmpeg, so the quality gate stays where it can run — in arc_service
// (vendored gate, app/services/radio_quality_gate.py) — and only
// gate-passed tracks are registered here. See README.md.

import { pickNext, queueStatus } from "./queue.js";
import {
  buildQueueState,
  findTrack,
  getHistory,
  getNowPlaying,
  getQueueState,
  getTracks,
  kvGetJson,
  kvPutJson,
  recordPlay,
  KEYS,
} from "./state.js";

// NOTE: do not add named exports here — workerd treats every named export
// as a handler entry and rejects plain values (e.g. a VERSION const breaks
// the deploy). Keep constants module-private.
const VERSION = "0.1.0";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Authorization, Content-Type",
};

function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...CORS, ...extraHeaders },
  });
}

function planned(what) {
  return json(
    {
      status: "planned",
      live: false,
      message: `TizWildin 24/7 Radio is not live yet — ${what} is not configured. See cloudflare/radio-worker/README.md.`,
    },
    503,
  );
}

function isLive(env) {
  return Boolean(env.STREAM_LIVE_URL);
}

function checkAdmin(request, env) {
  const secret = env.RADIO_ADMIN_SECRET;
  if (!secret) return false;
  const auth = request.headers.get("Authorization") ?? "";
  return auth === `Bearer ${secret}`;
}

export default {
  async fetch(request, env, ctx) {
    try {
      const url = new URL(request.url);
      const path = url.pathname;

      if (request.method === "OPTIONS") {
        return new Response(null, { status: 204, headers: CORS });
      }

      if (path === "/" || path === "/health") {
        return json({ status: "ok", service: "tizwildin-radio", version: VERSION, live: isLive(env) });
      }

      if (path === "/now-playing" && request.method === "GET") {
        const nowPlaying = await getNowPlaying(env.RADIO_KV);
        if (!nowPlaying) {
          return json({ status: "offline", nowPlaying: null, live: isLive(env) });
        }
        return json({ status: "streaming", nowPlaying, live: isLive(env) });
      }

      if (path === "/history" && request.method === "GET") {
        const limit = Math.min(Math.max(parseInt(url.searchParams.get("limit") ?? "50", 10) || 50, 1), 200);
        return json({ history: await getHistory(env.RADIO_KV, limit) });
      }

      if (path === "/queue" && request.method === "GET") {
        const state = (await getQueueState(env.RADIO_KV)) ?? (await buildQueueState(env.RADIO_KV));
        const nowPlaying = await getNowPlaying(env.RADIO_KV);
        return json(queueStatus(state, nowPlaying));
      }

      if (path === "/tracks" && request.method === "GET") {
        return json(await getTracks(env.RADIO_KV));
      }

      if (path === "/stream.m3u8" && request.method === "GET") {
        // True-live shape: hand the listener to Stream Live HLS.
        // While no live input exists this is an honest 503, not a fake stream.
        if (!env.STREAM_LIVE_URL) return planned("the Stream Live input");
        return Response.redirect(env.STREAM_LIVE_URL, 302);
      }

      const songMatch = path.match(/^\/song\/([^/]+)$/);
      if (songMatch && request.method === "GET") {
        if (!env.RADIO_AUDIO) return planned("the R2 audio bucket");
        const track = await findTrack(env.RADIO_KV, decodeURIComponent(songMatch[1]));
        if (!track) return json({ error: "track_not_found" }, 404);
        const key = track.r2Key ?? track.id;
        const range = request.headers.get("Range");
        const obj = range
          ? await env.RADIO_AUDIO.get(key, { range: parseRange(range) })
          : await env.RADIO_AUDIO.get(key);
        if (!obj) return json({ error: "audio_not_found" }, 404);
        const headers = {
          "Content-Type": obj.httpMetadata?.contentType ?? "audio/mpeg",
          "Accept-Ranges": "bytes",
          "Cache-Control": "public, max-age=86400",
          ...CORS,
        };
        if (obj.range) {
          headers["Content-Range"] = `bytes ${obj.range.offset}-${obj.range.offset + obj.range.length - 1}/${obj.size}`;
          return new Response(obj.body, { status: 206, headers });
        }
        return new Response(obj.body, { headers });
      }

      if (path === "/admin/advance" && request.method === "POST") {
        if (!checkAdmin(request, env)) return json({ error: "unauthorized" }, 401);
        const state = await buildQueueState(env.RADIO_KV);
        const { trackId, source, state: nextState } = pickNext(state);
        if (!trackId) {
          await kvPutJson(env.RADIO_KV, KEYS.NOW_PLAYING, null);
          return json({ status: "idle", nowPlaying: null, message: "Queue is empty — no tracks registered." });
        }
        const track = await findTrack(env.RADIO_KV, trackId);
        const entry = {
          file: track?.r2Key ?? trackId,
          title: track?.title ?? trackId,
          artist: track?.artist ?? "TizWildin",
          source,
          played_at: new Date().toISOString(),
        };
        await recordPlay(env.RADIO_KV, entry, nextState);
        return json({ status: "streaming", nowPlaying: entry });
      }

      if (path === "/admin/tracks" && request.method === "POST") {
        if (!checkAdmin(request, env)) return json({ error: "unauthorized" }, 401);
        const body = await request.json();
        const registry = {
          playlist: Array.isArray(body.playlist) ? body.playlist : [],
          submissions: Array.isArray(body.submissions) ? body.submissions : [],
        };
        await kvPutJson(env.RADIO_KV, KEYS.TRACKS, registry);
        // Reset queue progress — the track lists changed.
        await kvPutJson(env.RADIO_KV, KEYS.QUEUE_STATE, null);
        return json({ status: "ok", playlist: registry.playlist.length, submissions: registry.submissions.length });
      }

      return json({ error: "not_found" }, 404);
    } catch (err) {
      return json({ error: "internal_error", message: String(err?.message ?? err) }, 500);
    }
  },
};

function parseRange(header) {
  // "bytes=0-1023" -> { offset: 0, length: 1024 }. Open-ended "bytes=512-" supported.
  const m = /^bytes=(\d+)-(\d*)$/.exec(header.trim());
  if (!m) return undefined;
  const offset = parseInt(m[1], 10);
  const length = m[2] ? parseInt(m[2], 10) - offset + 1 : undefined;
  return length ? { offset, length } : { offset };
}
