#!/usr/bin/env bash
set -euo pipefail

# Package TizWildinHub VST3 + AU into a macOS .dmg installer.
# Usage: ./package_macos.sh [build_dir]
# build_dir defaults to ./build

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${1:-$ROOT/build}"
ARTEFACTS="$BUILD_DIR/TizWildinHub_artefacts/Release"
VERSION=$(grep 'project(TizWildinHub' "$ROOT/CMakeLists.txt" | sed 's/.*VERSION \([0-9.]*\).*/\1/')
DMG_NAME="TizWildinHub-v${VERSION}-macOS"
STAGING="$BUILD_DIR/dmg_staging"

echo "=== Packaging TizWildinHub v${VERSION} for macOS ==="

# Verify artefacts exist
VST3="$ARTEFACTS/VST3/TizWildinHub.vst3"
AU="$ARTEFACTS/AU/TizWildinHub.component"
STANDALONE="$ARTEFACTS/Standalone/TizWildinHub.app"

if [ ! -d "$VST3" ]; then
  echo "ERROR: VST3 not found at $VST3"
  echo "Run ./build_macos.sh first."
  exit 1
fi

# Clean staging area
rm -rf "$STAGING"
mkdir -p "$STAGING"

# Copy plugins
cp -R "$VST3" "$STAGING/"
if [ -d "$AU" ]; then
  cp -R "$AU" "$STAGING/"
fi
if [ -d "$STANDALONE" ]; then
  cp -R "$STANDALONE" "$STAGING/"
fi

# Create a README for the DMG
cat > "$STAGING/README.txt" << 'EOF'
TizWildinHub — Plugin Hub for TizWildin Entertainment
======================================================

INSTALLATION
------------
VST3:
  Drag TizWildinHub.vst3 to:
    ~/Library/Audio/Plug-Ins/VST3/

AU (Audio Unit):
  Drag TizWildinHub.component to:
    ~/Library/Audio/Plug-Ins/Components/

Standalone:
  Drag TizWildinHub.app to /Applications (optional).

Then rescan plugins in your DAW:
  - Ableton Live: Preferences → Plug-ins → Rescan
  - Logic Pro: Automatic detection
  - FL Studio: Options → Manage plugins → Find plugins

The plugin will appear under "TizWildin Entertainment" in your
DAW's plugin browser — alongside FreeEQ8 and the rest of the catalog.

https://github.com/GareBear99/TizWildinEntertainmentHUB
License: MIT
EOF

# Remove any existing DMG
rm -f "$BUILD_DIR/${DMG_NAME}.dmg"

# Create DMG
echo "Creating DMG..."
hdiutil create \
  -volname "TizWildinHub v${VERSION}" \
  -srcfolder "$STAGING" \
  -ov \
  -format UDZO \
  "$BUILD_DIR/${DMG_NAME}.dmg"

# Clean up staging
rm -rf "$STAGING"

echo ""
echo "✅ DMG created: $BUILD_DIR/${DMG_NAME}.dmg"
echo "   Size: $(du -h "$BUILD_DIR/${DMG_NAME}.dmg" | cut -f1)"
