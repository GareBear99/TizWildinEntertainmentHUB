# Branch Protection Rules

Recommended GitHub branch protections for this repo.

## `main`

- Require pull request before merge.
- Require status checks: `public-index` and `branch-map`.
- Require conversation resolution.
- Require linear history if available.
- Do not allow force pushes.
- Do not allow deletion.

## `develop`

- Require public index validation.
- Require branch-map validation.
- Allow squash merges from feature branches.

## Feature branches

Allowed prefixes: `seo/`, `submission/`, `route/`, `arc/`, `audio/`, `release/`, `hotfix/`. Reject untracked work when it does not fit one of these categories.
