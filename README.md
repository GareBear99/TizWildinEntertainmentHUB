# TizWildin Hub + ARC Package

A full scaffold for a JUCE-based plugin hub backed by ARC as the authority layer.

## Purpose

This package turns the earlier planning into a repo-ready implementation scaffold:

- **ARC service** for product truth, entitlements, seats, receipts, proposals, and authority decisions
- **JUCE hub scaffold** for desktop UI, refresh/install-missing/update flows, and account surfaces
- **Plugin bridge** for thin client authorization checks inside plugins
- **Stripe wiring docs** for one-time products, Complete Collection, and extra seat billing
- **Canonical manifests and schemas** for your product lineup

## Product organization

### Independent Headline Products
- FreeEQ8
- Therum
- WURP
- AETHER
- WhisperGate
- PaintMask

### Maid Suite
- BassMaid
- GlueMaid
- SpaceMaid
- MixMaid

### RiftWave Suite
- WaveForm / RiftSynth Lite
- WaveForm Pro
- RiftSynth Pro

## Seats
- Extra seats: **$3/month per seat**
- Max extra seats: **9**
- Base policy: ownership and seat count are separate

## Key rule

**Stripe bills. ARC decides. Hub operates. Plugins ask.**

## Package layout

```text
TizWildin_Hub_ARC_Package/
├── README.md
├── docs/
├── manifests/
├── schemas/
├── arc_service/
├── hub_scaffold/
├── plugin_bridge/
├── stripe/
└── scripts/
```

## What is production-ready vs scaffold

This package is a serious implementation scaffold, not a fully shipped commercial product.

### Included now
- canonical product catalog
- schema definitions
- FastAPI ARC service skeleton
- local mock data store
- proposal / authority service logic
- seat allocation logic
- JUCE hub class/file scaffold
- plugin bridge interface scaffold
- Stripe integration plan and mapping files

### Still required later
- real persistence layer
- real GitHub release polling
- real installer actions
- Stripe secret/backend deployment
- JUCE project generation and UI skinning
- plugin host runtime integration tests

## Fast start

### ARC service
```bash
cd arc_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Hub scaffold
Open the `hub_scaffold` directory in your JUCE workflow and wire it into Projucer/CMake.

## Suggested repo split
- `TizWildinHub` -> JUCE desktop app
- `TizWildinHub-ARC` -> Python authority service
- `TizWildinPluginBridge` -> shared JUCE/C++ client module
