// Worker endpoint tests — in-memory KV/R2 stubs, no Cloudflare needed.
// Run: node --test test/  (or: npm test)
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";

// Minimal KV stub: get(key, "json") / put(key, string).
class MemoryKV {
  constructor() {
    this.store = new Map();
  }
  async get(key, type) {
    const raw = this.store.get(key);
    if (raw === undefined) return null;
    return type === "json" ? JSON.parse(raw) : raw;
  }
  async put(key, value) {
    this.store.set(key, value);
  }
}

// Minimal R2 stub: get(key) -> { body, httpMetadata, size } | null.
class MemoryR2 {
  constructor(files = {}) {
    this.files = files; // key -> { body: string, contentType }
  }
  async get(key, opts) {
    const f = this.files[key];
    if (!f) return null;
    const bytes = new TextEncoder().encode(f.body);
    let body = bytes;
    let range;
    if (opts?.range) {
      const { offset, length } = opts.range;
      const end = length ? offset + length : bytes.length;
      body = bytes.slice(offset, end);
      range = { offset, length: body.length };
    }
    return {
      body,
      size: bytes.length,
      range,
      httpMetadata: { contentType: f.contentType ?? "audio/mpeg" },
    };
  }
}

function makeEnv(overrides = {}) {
  return {
    RADIO_KV: new MemoryKV(),
    RADIO_AUDIO: undefined,
    STREAM_LIVE_URL: "",
    RADIO_ADMIN_SECRET: "test-secret",
    ...overrides,
  };
}

async function call(env, path, opts = {}) {
  const req = new Request(`https://tizwildin-radio.admension.workers.dev${path}`, opts);
  const res = await worker.fetch(req, env, {});
  const text = await res.text();
  let body = null;
  try {
    body = JSON.parse(text);
  } catch {
    body = text;
  }
  return { status: res.status, headers: res.headers, body, text };
}

const ADMIN = { headers: { Authorization: "Bearer test-secret", "Content-Type": "application/json" } };

test("health reports version and not-live while Stream is unconfigured", async () => {
  const { status, body } = await call(makeEnv(), "/health");
  assert.equal(status, 200);
  assert.equal(body.service, "tizwildin-radio");
  assert.equal(body.version, "0.1.0");
  assert.equal(body.live, false);
});

test("now-playing is offline with an empty KV", async () => {
  const { status, body } = await call(makeEnv(), "/now-playing");
  assert.equal(status, 200);
  assert.equal(body.status, "offline");
  assert.equal(body.nowPlaying, null);
});

test("stream.m3u8 is an honest 503 while no live input exists", async () => {
  const { status, body } = await call(makeEnv(), "/stream.m3u8");
  assert.equal(status, 503);
  assert.equal(body.status, "planned");
  assert.equal(body.live, false);
});

test("stream.m3u8 redirects to the Stream Live URL when configured", async () => {
  const env = makeEnv({ STREAM_LIVE_URL: "https://customer-xyz.cloudflarestream.com/abc/manifest/video.m3u8" });
  const res = await worker.fetch(
    new Request("https://tizwildin-radio.admension.workers.dev/stream.m3u8"),
    env,
    {},
  );
  assert.equal(res.status, 302);
  assert.equal(res.headers.get("Location"), env.STREAM_LIVE_URL);
});

test("song endpoint is an honest 503 while R2 is unbound", async () => {
  const { status, body } = await call(makeEnv(), "/song/track-1");
  assert.equal(status, 503);
  assert.equal(body.status, "planned");
});

test("song endpoint serves R2 bytes when bound, 404 for unknown tracks", async () => {
  const env = makeEnv({
    RADIO_AUDIO: new MemoryR2({ "audio/track-1.mp3": { body: "FAKEAUDIO" } }),
  });
  await call(env, "/admin/tracks", {
    method: "POST",
    ...ADMIN,
    body: JSON.stringify({
      playlist: [{ id: "track-1", title: "Test Track", artist: "TizWildin", source: "playlist", r2Key: "audio/track-1.mp3" }],
      submissions: [],
    }),
  });
  const ok = await worker.fetch(new Request("https://tizwildin-radio.admension.workers.dev/song/track-1"), env, {});
  assert.equal(ok.status, 200);
  assert.equal(await ok.text(), "FAKEAUDIO");
  const missing = await call(env, "/song/nope");
  assert.equal(missing.status, 404);
});

test("admin routes require the Bearer secret", async () => {
  const env = makeEnv();
  const { status } = await call(env, "/admin/advance", { method: "POST" });
  assert.equal(status, 401);
});

test("advance: submission first, then playlist; now-playing + history follow", async () => {
  const env = makeEnv();
  await call(env, "/admin/tracks", {
    method: "POST",
    ...ADMIN,
    body: JSON.stringify({
      playlist: [
        { id: "p1", title: "Playlist One", artist: "TizWildin", source: "playlist", r2Key: "audio/p1.mp3" },
        { id: "p2", title: "Playlist Two", artist: "TizWildin", source: "playlist", r2Key: "audio/p2.mp3" },
      ],
      submissions: [{ id: "s1", title: "Sub One", artist: "Fan", source: "submission", r2Key: "audio/s1.mp3" }],
    }),
  });

  // Empty queue first: advance with nothing registered reports idle.
  const emptyEnv = makeEnv();
  const idle = await call(emptyEnv, "/admin/advance", { method: "POST", ...ADMIN });
  assert.equal(idle.body.status, "idle");

  const first = await call(env, "/admin/advance", { method: "POST", ...ADMIN });
  assert.equal(first.status, 200);
  assert.equal(first.body.nowPlaying.title, "Sub One");
  assert.equal(first.body.nowPlaying.source, "submission");

  const second = await call(env, "/admin/advance", { method: "POST", ...ADMIN });
  assert.equal(second.body.nowPlaying.source, "playlist");
  assert.ok(["Playlist One", "Playlist Two"].includes(second.body.nowPlaying.title));

  const np = await call(env, "/now-playing");
  assert.equal(np.body.status, "streaming");
  assert.equal(np.body.nowPlaying.title, second.body.nowPlaying.title);

  const history = await call(env, "/history?limit=10");
  assert.equal(history.body.history.length, 2);
  assert.equal(history.body.history[0].title, second.body.nowPlaying.title);
  assert.equal(history.body.history[1].title, "Sub One");

  const queue = await call(env, "/queue");
  assert.equal(queue.body.status, "streaming");
  assert.equal(queue.body.playlistLength, 2);
  assert.equal(queue.body.submissionsPending, 0);
  assert.equal(queue.body.nowPlaying.title, second.body.nowPlaying.title);
});
