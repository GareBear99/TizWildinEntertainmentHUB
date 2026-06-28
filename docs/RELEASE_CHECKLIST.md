# Release Checklist

Use this before tagging a public HUB release.

## Repo hygiene

- [ ] No `__pycache__`, `.pyc`, local SQLite auth DB, tokens, or private env files.
- [ ] README links open correctly.
- [ ] GitHub Pages docs load without console errors.
- [ ] `plugins.json` and `packs.json` validate as JSON.
- [ ] Public copy does not claim inactive payment/account systems are live.

## API check

```bash
cd arc_service
python -m pytest
```

## Pages check

```bash
python3 -m http.server 8080
# open http://localhost:8080/docs/
```

## Release notes template

```md
## TizWildin Entertainment HUB vX.Y.Z

- Public SEO landing page updates
- Plugin/sample catalog updates
- Release Vault / FreeEQ8 routing updates
- API/service changes
- Known limitations
```
