---
name: Branch task
about: Track one branch from the execution queue (docs/BRANCH_EXECUTION_QUEUE.md)
title: "Branch: "
labels: branch-task
---

## Branch

<!-- Branch name, e.g. submission/libhunt-arc-graph. Must use an approved prefix: seo/, submission/, route/, arc/, audio/, release/, hotfix/. -->

## Cluster

<!-- Cluster from docs/branch-map.json, e.g. ARC LibHunt. -->

## Purpose

<!-- What this branch delivers, in one or two sentences. -->

## Must pass before merge

- [ ] `python scripts/build_public_index.py`
- [ ] `python scripts/validate_public_index.py`
- [ ] `python scripts/validate_branch_map.py`
- [ ] Source manifests/docs updated, public index rebuilt, next action recorded

## Submissions (only for `submission/*` branches)

- [ ] Evidence note saved
- [ ] `STATUS_BOARD` updated

## Next branch after this one

<!-- e.g. submission/libhunt-tizwildin-audio-graph -->
