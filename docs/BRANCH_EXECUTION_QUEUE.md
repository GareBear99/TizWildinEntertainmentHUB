# Branch Execution Queue

This queue keeps the ecosystem work moving in controlled branches.

| Order | Branch | Cluster | Outcome |
|---:|---|---|---|
| 1 | `seo/public-index-v8-branching` | Public index governance | Branch map, validation, CI, public branch routes |
| 2 | `submission/libhunt-arc-graph` | ARC LibHunt | ARC-Neuron ↔ ARC-Core ↔ Lucifer Runtime ↔ Language Module ↔ Arc-RAR |
| 3 | `submission/libhunt-tizwildin-audio-graph` | TizWildin LibHunt | FreeEQ8 ↔ HUB ↔ FreeVox8 ↔ awesome-audio-plugins-dev |
| 4 | `route/github-topics-cleanup` | GitHub native SEO | Normalize topics across ARC and audio repos |
| 5 | `route/openhub-sourceforge` | Open-source indexing | Open Hub + SourceForge route records |
| 6 | `route/awesome-lists` | PR-based validation | Local AI, self-hosted, JUCE, audio DSP, music production list prep |
| 7 | `arc/source-spine-index` | ARC pages | Better public descriptions, relationship graph, routes |
| 8 | `audio/tizwildin-directory-index` | Audio pages | Audio directories, sample-pack routes, editorial review targets |
| 9 | `release/public-index-v8` | Release | Freeze, validate, publish |

A branch is complete only after it updates source manifests/docs, rebuilds the public index, passes validation, and records the next action.

## Branch 1 status (2026-11-07)

`seo/public-index-v8-branching` is open and in progress on its own branch (created from `main` at `c987fe8`). Most of its deliverable was already on `main` (branch-map.json, the four BRANCHING_*.md docs, `scripts/validate_branch_map.py`, the six public branch route pages). The missing pieces were delivered on this branch: `.github/workflows/branch-discipline.yml` (CI validation for branch map + public index), `.github/pull_request_template.md`, and `.github/ISSUE_TEMPLATE/branch-task.md` — the audit report had listed these as added, but they never existed in the repo. Public index rebuilt and all three validators pass on this branch.

## Next action

Open Branch 2: `submission/libhunt-arc-graph` — finish the ARC LibHunt alternatives graph (ARC-Neuron ↔ ARC-Core ↔ Lucifer Runtime ↔ Language Module ↔ Arc-RAR), with an evidence note saved and STATUS_BOARD updated before its status changes from queued to submitted.
