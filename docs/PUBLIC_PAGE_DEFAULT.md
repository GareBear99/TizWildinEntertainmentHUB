# Public Page Default

`docs/index.html` is intentionally the **V1 Public Dashboard**.

The newer SEO landing page is preserved at:

```text
docs/index-seo.html
```

GitHub Pages should be configured as:

```text
Settings → Pages → Deploy from branch → main → /docs
```

Expected public default:

```text
https://garebear99.github.io/TizWildinEntertainmentHUB/
```

That URL will load the V1 dashboard first, not the SEO landing page.

## V1 behavior

- Plugins tab is the default visible tab.
- Auto-check toggle defaults ON for first-time visitors.
- User choice is still respected through `localStorage.tiz_autocheck`.
