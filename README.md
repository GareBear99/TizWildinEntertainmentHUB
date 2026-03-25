# 🎛️ TizWildin Entertainment HUB

### The Free Modular Audio Plugin Ecosystem

> 12 free audio plugins — EQ, synths, instruments, effects — with a live update dashboard that checks GitHub releases in real time.

**🌐 [Open the Dashboard](https://garebear99.github.io/TizWildinEntertainmentHUB/)**

---

## 🚀 What This Is

A unified hub for the entire TizWildin plugin ecosystem:

- **Web Dashboard** — browse all plugins, check for updates, download latest releases
- **Live Version Checker** — hits GitHub Releases API to show 🟢 up to date, 🟡 new release, or 🔴 no release yet
- **Auto-check toggle** — enable auto-check on page load
- **One-click downloads** — direct links to GitHub release assets

No backend required. Runs entirely in the browser via GitHub Pages.

---

## 🧩 Plugin Ecosystem

### 🥇 Flagship Plugins

| Plugin | Description | Status |
|--------|-------------|--------|
| [**FreeEQ8**](https://github.com/GareBear99/FreeEQ8) | 8-band parametric EQ — dynamic EQ, linear phase, match EQ, M/S, spectrum analyzer | ✅ Production |
| [**PaintMask**](https://github.com/GareBear99/PaintMask_Free-JUCE-Plugin) | Visual paint-based audio processing — shape sound with brush strokes | ✅ Production |
| [**WURP**](https://github.com/GareBear99/WURP_Toxic-Motion-Engine_JUCE) | Toxic Motion Engine — formant motion, corrosive saturation, elastic pitch | ✅ Production |
| [**AETHER**](https://github.com/GareBear99/AETHER_Choir-Atmosphere-Designer) | Choir & atmosphere designer for cinematic sound | ⚠️ Beta |
| [**WhisperGate**](https://github.com/GareBear99/WhisperGate_Free-JUCE-Plugin) | Procedural whispers and ritual atmospheres via geometry | ✅ Production |
| [**Therum**](https://github.com/GareBear99/Therum_JUCE-Plugin) | Bootleg Serum — free wavetable synth | ✅ Production |

### 🧹 Maid Suite

| Plugin | Description | Status |
|--------|-------------|--------|
| [**BassMaid**](https://github.com/GareBear99/BassMaid) | Bass enhancement and low-end processing | ✅ Production |
| [**SpaceMaid**](https://github.com/GareBear99/SpaceMaid) | Spatial audio — depth, width, reverb | ✅ Production |
| [**GlueMaid**](https://github.com/GareBear99/GlueMaid) | Mix bus glue and cohesion | ✅ Production |
| [**MixMaid**](https://github.com/GareBear99/MixMaid) | All-in-one mixing utility toolkit | ✅ Production |

### 🔊 Sound Design & Experimental

| Plugin | Description | Status |
|--------|-------------|--------|
| [**RiftWave Suite**](https://github.com/GareBear99/RiftWaveSuite_RiftSynth_WaveForm_Lite) | Modular synth + waveform synthesis | ⚠️ Beta |
| [**FreeSampler**](https://github.com/GareBear99/FreeSampler_v0.3) | Lightweight audio sampler plugin | 🚧 Dev |

---

## 🌐 Dashboard

The web dashboard at **[garebear99.github.io/TizWildinEntertainmentHUB](https://garebear99.github.io/TizWildinEntertainmentHUB/)** provides:

- **Plugin cards** grouped by category with descriptions and format badges
- **Live version status** per plugin:
  - 🟢 **Green** — latest release tag and age
  - 🟡 **Yellow "NEW RELEASE"** — released within the last 7 days
  - 🔴 **Red "NO RELEASE YET"** — source available but no binary release
- **Download buttons** — links directly to GitHub release assets
- **Auto-check toggle** — remembered in localStorage

The dashboard reads from [`plugins.json`](plugins.json) and fetches release data from the GitHub API (unauthenticated, 60 requests/hour).

---

## 📁 Repository Structure

```
TizWildinEntertainmentHUB/
├── docs/index.html          # Web dashboard (GitHub Pages)
├── plugins.json             # Plugin manifest (source of truth)
├── arc_service/             # FastAPI backend (future infrastructure)
├── hub_app/                 # JUCE desktop app (future infrastructure)
├── hub_scaffold/            # JUCE app scaffold
├── plugin_bridge/           # C++ bridge for plugin communication
├── manifests/               # Product catalog & Stripe mapping
├── schemas/                 # JSON schemas
├── scripts/                 # Python utility scripts
└── docs/                    # Architecture & quickstart docs
```

---

## ⚡ Quick Start

### Use the Dashboard (recommended)
Visit **[garebear99.github.io/TizWildinEntertainmentHUB](https://garebear99.github.io/TizWildinEntertainmentHUB/)** → click "Check All Updates" → download plugins.

### Add a Plugin
Edit `plugins.json` and add an entry:
```json
{
  "id": "myplugin",
  "name": "MyPlugin",
  "description": "What it does.",
  "category": "flagship",
  "repo": "MyPlugin-Repo-Name",
  "license": "FREE",
  "formats": ["VST3", "AU"],
  "status": "production"
}
```
The dashboard will automatically pick it up and check for releases.

---

## 🛣️ Roadmap

- [ ] Create GitHub releases for all plugins (currently only FreeEQ8 has releases)
- [ ] Add CI/CD build pipelines per plugin
- [ ] Desktop HUB app (JUCE) with local install/update capability
- [ ] Plugin preset sharing via the HUB

---

## ⭐ Support

All plugins are **free**. Star the repos you use:

- [TizWildinEntertainmentHUB](https://github.com/GareBear99/TizWildinEntertainmentHUB) — this repo
- [FreeEQ8](https://github.com/GareBear99/FreeEQ8) — flagship EQ
- [awesome-audio-plugins-dev](https://github.com/GareBear99/awesome-audio-plugins-dev) — curated list of 50+ free audio tools

Built with ❤️ by Gary Doman (GareBear99 / TizWildin)

*"Great sound shouldn't cost anything."*
