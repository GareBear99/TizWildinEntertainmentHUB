# Branch Release Ladder

## Normal release flow

```text
seo/*, submission/*, route/*, arc/*, audio/*
        ↓
      develop
        ↓
release/public-index-vX
        ↓
      main
```

## Hotfix flow

```text
hotfix/public-link-or-sitemap-fix
        ↓
      main
        ↓
      develop
```

## Release freeze checklist

- `CHANGELOG.md` updated.
- `docs/SEO_BUILD_REPORT.json` regenerated.
- `docs/public-index.json` regenerated.
- `docs/sitemap.xml` regenerated.
- `docs/llms.txt` regenerated.
- `docs/PUBLIC_LINK_GRAPH.md` regenerated.
- `docs/branch-map.json` validates.
- No cache/dev artifacts.
- Every new route has a static page and sitemap URL.
