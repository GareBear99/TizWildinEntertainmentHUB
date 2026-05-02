# V1 / Free-Version Toggle Default

This package is based on the user's previous default package, not the newer SEO-default package.

`docs/index.html` remains the default V1 public dashboard.

Behavior:

- First visit: auto-check is ON.
- If the user turns it OFF: `localStorage.tiz_autocheck = "false"` and the dashboard respects it.
- If the user turns it back ON: `localStorage.tiz_autocheck = "true"`.

Native JUCE hub behavior is aligned:

```cpp
return props->getBoolValue ("autoUpdate", true);
```
