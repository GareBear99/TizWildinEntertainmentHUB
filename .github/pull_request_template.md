## Branch

<!-- Branch name, e.g. seo/public-index-v8-branching. Must use an approved prefix: seo/, submission/, route/, arc/, audio/, release/, hotfix/. See docs/BRANCHING_STRATEGY.md. -->

## Purpose

<!-- What this branch delivers, in one or two sentences. -->

## Branch-map update

- [ ] `docs/branch-map.json` updated (status, purpose, mustPass) if this branch changes the queue
- [ ] Queue order in `docs/BRANCH_EXECUTION_QUEUE.md` still matches `docs/branch-map.json`

## Public index

- [ ] Source manifests/docs updated first
- [ ] Public index rebuilt: `python scripts/build_public_index.py`
- [ ] `python scripts/validate_public_index.py` passes
- [ ] `python scripts/validate_branch_map.py` passes
- [ ] No generated page hand-edited unless the generator was updated or the file is intentionally static

## Submissions (only for `submission/*` branches)

- [ ] Evidence note saved before status changes from queued to submitted
- [ ] `STATUS_BOARD` updated

## Next action

<!-- The next branch to open after this one merges, e.g. submission/libhunt-arc-graph. -->
