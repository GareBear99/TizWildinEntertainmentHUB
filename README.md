# TizWildinEntertainment HUB v1.3

This package is a stronger local-commercial baseline for your plugin hub. v1.3 adds:
- local account registration/login/refresh/me endpoints backed by SQLite
- local checkout session + entitlement mutation flow for owned plugins and extra seats
- release manifest import from local JSON or URL
- remote/file artifact download support in execute flow
- expanded tests for local auth, billing, and imported release installs

# TizWildinEntertainment HUB v1.0

This package is the **local-complete hub demo baseline**. It is still a mock/control-plane build rather than a live commercial deployment, but it now has a one-command demo bootstrap, a consolidated launchpad endpoint, Docker support, backup/restore, diagnostics export, staged local artifacts, mock install execution, rollback, uninstall, and repair flows.

See `docs/QUICKSTART.md` for the fastest local boot path.

# TizWildinEntertainmentHUB v0.9

Operator-grade mock control plane for a JUCE plugin hub backed by the ARC authority service.

## What is new in v0.9
- preflight endpoint for one-shot readiness checks before staging or execution
- backup export / restore flow for full mock service state snapshots
- hub UI scaffold now exposes Stage, Preflight, Execute, and Backup actions
- helper scripts added for manual backup and restore
- package cleaned so test/cache junk is not shipped

## Current lifecycle covered
account -> entitlements -> seats -> install plan -> staged artifacts -> download plan -> execute -> receipts -> machine inventory -> uninstall / repair / rollback -> diagnostics -> backups

## Included folders
- `arc_service/` FastAPI ARC backend
- `hub_app/` JUCE desktop scaffold
- `plugin_bridge/` runtime validation bridge scaffold
- `manifests/` catalog and Stripe mapping mock data
- `scripts/` helper scripts for demo flows
- `artifacts/` staged demo packages, diagnostics, backups
- `docs/` readiness and architecture notes

## Run ARC locally
```bash
cd arc_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test ARC
```bash
cd arc_service
pytest -q
```

## Not finished yet
This package is stronger, but still not retail-complete. The biggest unfinished areas are still real auth, real Stripe purchase flows, remote updater/install delivery, code signing/notarization, and final production UI polish/build verification.


## v1.2 additions
- persisted hub settings endpoint and state file
- readiness endpoint for account+machine launch status
- activity feed endpoint for receipts + webhook history
- launchpad now includes persisted settings


## New in v1.2

- one-shot `/sync` endpoint for launchpad + readiness + preflight + install/download planning
- `/audit/{account}` endpoint for quick operator-grade readiness scoring
- `/support/bundle/{account}` endpoint that packages diagnostics + backup + support snapshot into one zip
- package cleanup: removed shipped cache folders from the deliverable
- ARC service version advanced to 1.2.0

# TizWildinEntertainment HUB

Universal launcher and update manager for the TizWildin audio plugin ecosystem.

Installs, updates, and manages:

• FreeEQ8
• WhisperGate
• PaintMask
• WURP
• WaveForm / RiftSynth
• future plugins

Built with a modular ARC control system inspired by the ARC intelligence system from the series Continuum.

---

## Features

✔ Plugin installer / updater  
✔ Seat licensing system  
✔ Machine registration  
✔ Artifact verification (SHA256)  
✔ Rollback and repair  
✔ Plugin entitlement system  
✔ Update channels (stable / beta)  
✔ Support diagnostics bundles  
✔ Local demo server included  

---

## Ecosystem

Plugins supported by the HUB:

| Plugin | Type |
|------|------|
| FreeEQ8 | Professional EQ |
| WhisperGate | Ritual Whisper FX |
| PaintMask | Paint-to-MIDI generator |
| WURP | Toxic gas modulation FX |
| WaveForm / RiftSynth | audio-reactive synth system |

---

## Architecture

The hub is powered by **ARC**, a control-plane service that manages:

- accounts
- entitlements
- installs
- machines
- artifacts
- diagnostics

ARC was conceptually inspired by the global surveillance AI **ARC** from the TV series *Continuum*.

---
