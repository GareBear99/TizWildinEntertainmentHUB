// Queue selection — pure logic, no Cloudflare APIs.
//
// Ported from radio_service/queue_manager.py (RadioQueue):
//   1. Submissions take priority, first-in-first-out, each played ONCE.
//      A played submission is never re-queued (the Python side tracks
//      played filenames in history; here we track played ids in state).
//   2. Otherwise the playlist plays in a shuffled order with no repeat
//      until every track has played, then it reshuffles.
//   3. Nothing available -> null.
//
// The state object is plain JSON so it can live in KV verbatim:
//   {
//     playlist:    [trackId, ...],   // all known playlist track ids
//     submissions: [trackId, ...],   // pending submission ids, FIFO
//     order:       [trackId, ...],   // current shuffled playlist order
//     index:       0,                // next position in `order`
//     playedSubmissions: [trackId, ...]
//   }
//
// `rng` is injectable so tests can run deterministically.

export function createQueueState(playlistIds = [], submissionIds = [], rng = Math.random) {
  const state = {
    playlist: [...playlistIds],
    submissions: [...submissionIds],
    order: shuffle([...playlistIds], rng),
    index: 0,
    playedSubmissions: [],
  };
  return state;
}

export function shuffle(list, rng = Math.random) {
  const arr = [...list];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

/**
 * Pick the next track. Returns { trackId, source, state } where source is
 * "submission" | "playlist", or { trackId: null, source: null, state } when
 * the queue is empty. The returned state is the new state to persist.
 */
export function pickNext(state, rng = Math.random) {
  const next = {
    playlist: [...(state.playlist ?? [])],
    submissions: [...(state.submissions ?? [])],
    order: [...(state.order ?? [])],
    index: state.index ?? 0,
    playedSubmissions: [...(state.playedSubmissions ?? [])],
  };

  // 1. Submissions first (FIFO, once each).
  while (next.submissions.length > 0) {
    const id = next.submissions.shift();
    if (next.playedSubmissions.includes(id)) continue;
    next.playedSubmissions.push(id);
    return { trackId: id, source: "submission", state: next };
  }

  // 2. Shuffled playlist, no repeat until exhausted, then reshuffle.
  if (next.playlist.length === 0) {
    return { trackId: null, source: null, state: next };
  }
  if (next.order.length === 0 || next.index >= next.order.length) {
    next.order = shuffle([...next.playlist], rng);
    next.index = 0;
  }
  // Drop stale order entries (tracks removed from the playlist since).
  while (next.index < next.order.length && !next.playlist.includes(next.order[next.index])) {
    next.index += 1;
  }
  if (next.index >= next.order.length) {
    next.order = shuffle([...next.playlist], rng);
    next.index = 0;
  }
  const trackId = next.order[next.index];
  next.index += 1;
  return { trackId, source: "playlist", state: next };
}

/** Remove a track id from the playlist (and from the current order). */
export function removeFromPlaylist(state, trackId) {
  return {
    ...state,
    playlist: (state.playlist ?? []).filter((id) => id !== trackId),
    order: (state.order ?? []).filter((id) => id !== trackId),
  };
}

/** Queue status in the same shape as radio_service's /app/data/queue.json,
 *  so the Pages player and ARC can consume either source unchanged. */
export function queueStatus(state, nowPlaying) {
  return {
    status: nowPlaying ? "streaming" : "idle",
    nowPlaying: nowPlaying ?? null,
    submissionQueue: [...(state.submissions ?? [])],
    queueLength: (state.submissions ?? []).length,
    playlistLength: (state.playlist ?? []).length,
    submissionsPending: (state.submissions ?? []).length,
    updatedAt: new Date().toISOString(),
  };
}
