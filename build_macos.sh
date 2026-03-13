#!/usr/bin/env bash
set -euo pipefail

# Build TizWildinHub for macOS (Xcode toolchain).
# Requires: cmake, Xcode command line tools, JUCE as ./JUCE submodule or -DJUCE_DIR=...
#
# After build, COPY_PLUGIN_AFTER_BUILD will install:
#   VST3  → ~/Library/Audio/Plug-Ins/VST3/TizWildinHub.vst3
#   AU    → ~/Library/Audio/Plug-Ins/Components/TizWildinHub.component
#
# Rescan plugins in your DAW → find "TizWildinHub" under TizWildin Entertainment.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# Ensure JUCE submodule is initialized
if [ ! -f "JUCE/CMakeLists.txt" ]; then
    echo "Initializing JUCE submodule..."
    git submodule update --init --recursive
    (cd JUCE && git checkout 7.0.12)
fi

mkdir -p build
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release

echo ""
echo "Build finished."
echo "Look in build/ for the plugin artifacts (VST3/AU/Standalone)."
echo ""
echo "Plugin installed to:"
echo "  VST3: ~/Library/Audio/Plug-Ins/VST3/TizWildinHub.vst3"
echo "  AU:   ~/Library/Audio/Plug-Ins/Components/TizWildinHub.component"
echo ""
echo "Rescan plugins in your DAW to find TizWildinHub under TizWildin Entertainment."
