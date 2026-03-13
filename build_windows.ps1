# Build TizWildinHub for Windows (Visual Studio generator via CMake).
# Requires: CMake, Visual Studio Build Tools, JUCE as ./JUCE submodule OR set JUCE_DIR env var.
#
# After build, COPY_PLUGIN_AFTER_BUILD will install VST3 to the system directory.
# Rescan plugins in your DAW → find "TizWildinHub" under TizWildin Entertainment.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

# Ensure JUCE submodule is initialized
if (!(Test-Path "JUCE\CMakeLists.txt")) {
    Write-Host "Initializing JUCE submodule..."
    git submodule update --init --recursive
    Push-Location JUCE
    git checkout 7.0.12
    Pop-Location
}

if (!(Test-Path "build")) { New-Item -ItemType Directory -Path "build" | Out-Null }

cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release

Write-Host ""
Write-Host "Build finished. Look in build/ for VST3 output."
Write-Host ""
Write-Host "To install manually, copy TizWildinHub.vst3 to:"
Write-Host "  C:\Program Files\Common Files\VST3\"
Write-Host ""
Write-Host "Rescan plugins in your DAW to find TizWildinHub under TizWildin Entertainment."
