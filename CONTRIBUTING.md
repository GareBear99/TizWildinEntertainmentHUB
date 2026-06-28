# Contributing

Contributions are welcome when they improve trust, usability, docs, catalog accuracy, or code quality.

## Priorities

1. Fix broken links and public routing.
2. Improve plugin/sample catalog metadata.
3. Keep public copy honest.
4. Improve tests and service reliability.
5. Avoid hype claims that are not backed by live functionality.

## Local checks

```bash
python3 -m json.tool plugins.json >/dev/null
python3 -m json.tool packs.json >/dev/null
cd arc_service && python -m pytest
```
