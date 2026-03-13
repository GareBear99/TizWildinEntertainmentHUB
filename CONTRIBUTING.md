# Contributing to TizWildin Entertainment Hub

Thanks for helping improve the Hub + ARC ecosystem. This guide covers how to report issues, propose features, and submit pull requests.

## Code of Conduct

By participating in this project, you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to Contribute

### Report Bugs

Before opening a bug report:
- Search existing issues to avoid duplicates.
- Confirm the issue still reproduces on the latest commit.

When filing a bug, include:
- Environment (macOS/Windows/Linux, Python version)
- ARC service version/commit hash
- Exact steps to reproduce
- Expected behavior vs actual behavior
- Relevant logs / traceback
- Request + response payload examples (if API-related)

### Suggest Features

Feature ideas are welcome. Please include:
- The user problem being solved
- Proposed behavior
- Any API changes required
- Backward compatibility concerns
- Alternatives considered

## Development Setup

```bash
git clone https://github.com/GareBear99/TizWildinEntertainmentHUB.git
cd TizWildinEntertainmentHUB/arc_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run locally:

```bash
uvicorn app.main:app --reload
```

## Running Tests and Lint

From `arc_service/`:

```bash
pytest -v
ruff check .
```

## Pull Request Process

1. Fork and create a branch:
   ```bash
   git checkout -b feat/your-change-name
   ```
2. Keep changes focused and atomic.
3. Add/update tests for behavior changes.
4. Run tests + lint locally before opening the PR.
5. Open a PR with:
   - Clear title
   - Summary of changes
   - Testing notes
   - Related issue references

## Commit Message Suggestions

- `feat: add ...` for new features
- `fix: ...` for bug fixes
- `docs: ...` for documentation changes
- `refactor: ...` for restructuring without behavior change
- `test: ...` for tests only
- `chore: ...` for maintenance

## Architecture Notes

Core principle:

> **Stripe bills. ARC decides. Hub operates. Plugins ask.**

When contributing, keep authorization decisions centralized in ARC. Avoid moving entitlement logic into plugin or UI clients.

## Security

Please do not open public issues for security vulnerabilities. See [SECURITY.md](SECURITY.md) for reporting instructions.

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
