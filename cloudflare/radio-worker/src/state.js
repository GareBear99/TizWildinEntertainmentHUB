// KV state helpers — thin wrappers so the Worker logic stays testable
// with an in-memory KV stub. Keys mirror the radio service's file layout:
//
//   now_playing   -> current track entry (same shape as history entries)
//   history       -> [entry, ...] newest first, max 200
//   tracks        -> { playlist: [{id,title,artist,source,r2Key}], submissions: [...] }
//   queue_state   -> queue.js state object (see src/queue.js)
//
// A track entry: { id, title, artist, source, r2Key, addedAt }.
// A history entry: { file, title, source, played_at } — same shape the
// radio service writes to /app/data/history.json.

export const KEYS = {
  NOW_PLAYING: "now_playing",
  HISTORY: "history",
  TRACKS: "tracks",
  QUEUE_STATE: "queue_state",
};

const MAX_HISTORY = 200;

export async function kvGetJson(kv, key, fallback) {
  const raw = await kv.get(key, "json");
  return raw ?? fallback;
}

export async function kvPutJson(kv, key, value) {
  await kv.put(key, JSON.stringify(value));
}

export async function getNowPlaying(kv) {
  return kvGetJson(kv, KEYS.NOW_PLAYING, null);
}

export async function getHistory(kv, limit = 50) {
  const history = await kvGetJson(kv, KEYS.HISTORY, []);
  return Array.isArray(history) ? history.slice(0, limit) : [];
}

export async function getTracks(kv) {
  const tracks = await kvGetJson(kv, KEYS.TRACKS, { playlist: [], submissions: [] });
  return {
    playlist: Array.isArray(tracks.playlist) ? tracks.playlist : [],
    submissions: Array.isArray(tracks.submissions) ? tracks.submissions : [],
  };
}

export async function getQueueState(kv) {
  return kvGetJson(kv, KEYS.QUEUE_STATE, null);
}

/** Record a play: set now-playing, prepend to history, persist queue state. */
export async function recordPlay(kv, entry, queueState) {
  await kvPutJson(kv, KEYS.NOW_PLAYING, entry);
  const history = await kvGetJson(kv, KEYS.HISTORY, []);
  history.unshift(entry);
  await kvPutJson(kv, KEYS.HISTORY, history.slice(0, MAX_HISTORY));
  if (queueState) {
    await kvPutJson(kv, KEYS.QUEUE_STATE, queueState);
  }
  return entry;
}

/** Build a queue.js state object from the KV track registry. */
export async function buildQueueState(kv, rng) {
  const { createQueueState } = await import("./queue.js");
  const tracks = await getTracks(kv);
  const existing = await getQueueState(kv);
  const playlistIds = tracks.playlist.map((t) => t.id);
  const submissionIds = tracks.submissions.map((t) => t.id);
  if (!existing) {
    return createQueueState(playlistIds, submissionIds, rng);
  }
  // Keep persisted progress (order/index/played) but refresh the track lists.
  return {
    playlist: playlistIds,
    submissions: submissionIds.filter((id) => !(existing.playedSubmissions ?? []).includes(id)),
    order: (existing.order ?? []).filter((id) => playlistIds.includes(id)),
    index: existing.index ?? 0,
    playedSubmissions: existing.playedSubmissions ?? [],
  };
}

/** Look a track id up in the registry (playlist first, then submissions). */
export async function findTrack(kv, trackId) {
  const tracks = await getTracks(kv);
  return (
    tracks.playlist.find((t) => t.id === trackId) ??
    tracks.submissions.find((t) => t.id === trackId) ??
    null
  );
}
