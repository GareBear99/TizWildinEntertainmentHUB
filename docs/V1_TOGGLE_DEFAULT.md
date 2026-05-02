# V1 / Free-Version Toggle Default

The dashboard auto-check toggle defaults **ON** for first-time visitors.

Behavior:

- First visit: auto-check is ON.
- If the user turns it OFF: `localStorage.tiz_autocheck = "false"` and the dashboard respects it.
- If the user turns it back ON: `localStorage.tiz_autocheck = "true"`.

Native JUCE hub behavior is aligned:

```cpp
return props->getBoolValue ("autoUpdate", true);
```

This preserves the V1/free-version dashboard as the default active update-check experience.
