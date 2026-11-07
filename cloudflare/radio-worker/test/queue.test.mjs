// Queue-selection tests — pure logic, no Cloudflare needed.
// Run: node --test test/  (or: npm test)
import test from "node:test";
import assert from "node:assert/strict";
import { createQueueState, pickNext, queueStatus, shuffle } from "../src/queue.js";

// Deterministic RNG (mulberry32) so shuffles are reproducible in tests.
function seededRng(seed) {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

test("submissions play first, FIFO, and only once each", () => {
  let state = createQueueState(["p1", "p2", "p3"], ["s1", "s2"], seededRng(1));
  let r = pickNext(state, seededRng(1));
  assert.equal(r.trackId, "s1");
  assert.equal(r.source, "submission");
  state = r.state;
  r = pickNext(state, seededRng(1));
  assert.equal(r.trackId, "s2");
  state = r.state;
  // Submissions exhausted — playlist next, and s1/s2 never come back.
  r = pickNext(state, seededRng(1));
  assert.equal(r.source, "playlist");
  assert.ok(["p1", "p2", "p3"].includes(r.trackId));
  state = r.state;
  const seen = new Set([r.trackId]);
  for (let i = 0; i < 10; i++) {
    r = pickNext(state, seededRng(1));
    state = r.state;
    assert.notEqual(r.trackId, "s1");
    assert.notEqual(r.trackId, "s2");
    seen.add(r.trackId);
  }
  assert.deepEqual([...seen].sort(), ["p1", "p2", "p3"]);
});

test("playlist plays every track once before reshuffling", () => {
  let state = createQueueState(["a", "b", "c", "d"], [], seededRng(7));
  const played = [];
  for (let i = 0; i < 4; i++) {
    const r = pickNext(state, seededRng(7));
    assert.equal(r.source, "playlist");
    played.push(r.trackId);
    state = r.state;
  }
  assert.deepEqual([...played].sort(), ["a", "b", "c", "d"]);
  // 5th pick starts a fresh shuffle — still a valid track, no crash.
  const r = pickNext(state, seededRng(7));
  assert.ok(["a", "b", "c", "d"].includes(r.trackId));
});

test("empty queue returns null", () => {
  const state = createQueueState([], [], seededRng(1));
  const r = pickNext(state, seededRng(1));
  assert.equal(r.trackId, null);
  assert.equal(r.source, null);
});

test("shuffle is a permutation (no drops, no duplicates)", () => {
  const out = shuffle(["a", "b", "c", "d", "e"], seededRng(42));
  assert.deepEqual([...out].sort(), ["a", "b", "c", "d", "e"]);
});

test("queueStatus matches the radio_service queue.json shape", () => {
  const state = createQueueState(["p1", "p2"], ["s1"], seededRng(1));
  const status = queueStatus(state, null);
  assert.equal(status.status, "idle");
  assert.equal(status.nowPlaying, null);
  assert.deepEqual(status.submissionQueue, ["s1"]);
  assert.equal(status.queueLength, 1);
  assert.equal(status.playlistLength, 2);
  assert.equal(status.submissionsPending, 1);
  assert.ok(status.updatedAt);
  const live = queueStatus(state, { file: "x.mp3", title: "x", source: "playlist", played_at: "2026-11-07T00:00:00Z" });
  assert.equal(live.status, "streaming");
});
