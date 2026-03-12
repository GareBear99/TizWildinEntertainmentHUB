# TizWildinEntertainmentHUB
# TizWildin Hub + ARC

The **TizWildin Hub** is the official desktop control center for the TizWildin plugin ecosystem.

It installs, updates, manages, and authorizes all plugins across the platform while integrating with **ARC**, the authority kernel responsible for product state, entitlements, receipts, and licensing decisions.

---

# Architecture

The ecosystem is intentionally separated into four layers.

## ARC (Authority Core)

ARC is the canonical authority layer.

ARC manages:

- Product catalog
- Entitlement ledger
- Seat licensing
- Payment receipts
- Install state
- Version state
- Proposal validation
- Authority decisions

ARC converts external events (Stripe payments, repo updates, hub scans) into deterministic system state.

---

## TizWildin Hub

The Hub is the desktop operator interface.

Responsibilities:

- Install plugins
- Check installed plugins
- Refresh product states
- Install missing plugins
- Check updates
- Manage seats
- Launch purchases
- Display product catalog
- Display version information
- Connect to ARC

The Hub never decides ownership itself — it asks ARC.

---

## Plugins

Plugins contain a very small **Plugin Bridge** module.

The bridge allows plugins to:

- report product ID
- report version
- check license authority
- open the hub for installs or upgrades

Plugins never process payments.

---

## Stripe

Stripe handles:

- one-time purchases
- subscriptions
- billing lifecycle
- seat subscriptions

ARC receives Stripe webhook events and converts them into receipts and entitlements.

---

# Product Structure

## Independent Headline Products

Standalone plugins.

- FreeEQ8
- Therum
- WURP
- AETHER
- WhisperGate
- PaintMask

WURP will later include:

- **WURP Toxicron Edition** (coming soon)

---

## Maid Suite

Mixing toolkit plugins.

- BassMaid
- GlueMaid
- SpaceMaid
- MixMaid

FreeEQ8 is not part of the Maid Suite.

---

## RiftWave Suite

Creative synth and visualization tools.

- WaveForm / RiftSynth Lite
- WaveForm Pro
- RiftSynth Pro

Internal frameworks are not shown in the hub UI.

---

# Seat System

Extra seats allow additional machines to use owned plugins.

Pricing model:


$3 per seat / month
maximum 9 extra seats


Seat rules:

- seats apply across the entire plugin ecosystem
- seats represent concurrent machines
- seats can be released manually
- inactive seats can expire automatically
- seat quantity is handled by Stripe subscription quantity

---

# Ownership Model

Ownership is separate from seats.

Ownership determines:

- which plugins a user can use

Seats determine:

- how many machines can run them simultaneously.

Special ownership flag:


ownsEveryVST


User-facing label:


Complete Collection


If this flag is present, all supported plugins unlock automatically.

---

# Hub Features

- product browser
- install checker
- install missing
- refresh system state
- update detection
- repo integration
- changelog display
- purchase prompts
- seat management
- billing portal access

---

# Plugin State Types

Plugins can appear as:

- Installed
- Not Installed
- Update Available
- Source Update Available
- Build Required
- Owned
- Free
- Coming Soon
- Experimental
- Archived

---

# Repository Layout


/arc
authority engine
product registry
entitlement engine
receipt ledger
stripe webhook handler

/hub
JUCE desktop application

/plugin_bridge
shared module embedded in plugins

/docs
architecture and schema definitions


---

# ARC Data Model

ARC tracks:

Product  
Edition  
Entitlement  
SeatSubscription  
SeatAssignment  
Receipt  
InstallState  
RepoState  
Proposal  
AuthorityDecision

All changes are recorded as events.

---

# Philosophy

Stripe bills.

ARC decides.

Hub operates.

Plugins ask.

---

# Status

Current stage:

Architecture scaffold.

Next phases:

- production ARC service
- Stripe webhook integration
- installer implementation
- plugin bridge integration
- hub UI completion

---

# License

TizWildin Entertainment
