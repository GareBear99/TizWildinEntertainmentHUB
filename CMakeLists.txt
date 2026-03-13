cmake_minimum_required(VERSION 3.15)
project(TizWildinHub VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 17)

# Universal binary for macOS (Intel + Apple Silicon)
if(APPLE)
  set(CMAKE_OSX_ARCHITECTURES "arm64;x86_64" CACHE STRING "Build universal binary")
  set(CMAKE_OSX_DEPLOYMENT_TARGET "10.13" CACHE STRING "Minimum macOS version")
endif()

# ---- JUCE ----
# Option A: JUCE as submodule in ./JUCE (recommended)
#   git submodule add https://github.com/juce-framework/JUCE.git JUCE
# Option B: Point JUCE_DIR to your local JUCE folder:
#   cmake -DJUCE_DIR=/path/to/JUCE ..
#
if (EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/JUCE/CMakeLists.txt")
  add_subdirectory(JUCE)
elseif (DEFINED JUCE_DIR AND EXISTS "${JUCE_DIR}/CMakeLists.txt")
  add_subdirectory("${JUCE_DIR}" JUCE)
else()
  message(FATAL_ERROR "JUCE not found. Add as submodule in ./JUCE or pass -DJUCE_DIR=/path/to/JUCE")
endif()

# ---- Plugin target ----
# This builds TizWildinHub as a VST3/AU plugin AND a standalone app.
# The plugin appears in DAWs under "TizWildin Entertainment" — the same
# manufacturer tab as FreeEQ8, Therum, WURP, and every other TizWildin plugin.
juce_add_plugin(TizWildinHub
  COMPANY_NAME            "TizWildinEntertainment"
  IS_SYNTH                FALSE
  NEEDS_MIDI_INPUT        FALSE
  NEEDS_MIDI_OUTPUT       FALSE
  IS_MIDI_EFFECT          FALSE
  COPY_PLUGIN_AFTER_BUILD TRUE
  PLUGIN_MANUFACTURER_CODE TzWd
  PLUGIN_CODE             TzHb
  FORMATS                 VST3 AU Standalone
  PRODUCT_NAME            "TizWildinHub"
  BUNDLE_ID               "com.tizwildinentertainment.hub"
  COMPANY_URL             "https://github.com/GareBear99/TizWildinEntertainmentHUB"
  COMPANY_EMAIL           "neovectr.inc@gmail.com"
  DESCRIPTION             "Plugin hub for the TizWildin Entertainment ecosystem"
)

target_sources(TizWildinHub PRIVATE
  hub_scaffold/Source/PluginProcessor.cpp
  hub_scaffold/Source/PluginProcessor.h
  hub_scaffold/Source/PluginEditor.h
  hub_scaffold/Source/TizHubMainComponent.cpp
  hub_scaffold/Source/TizHubMainComponent.h
  hub_scaffold/Source/ArcClient.cpp
  hub_scaffold/Source/ArcClient.h
  hub_scaffold/Source/TizHubState.h
)

target_include_directories(TizWildinHub PRIVATE
  hub_scaffold/Source
)

target_compile_definitions(TizWildinHub PRIVATE
  JUCE_WEB_BROWSER=0
  JUCE_USE_CURL=0
  JUCE_VST3_CAN_REPLACE_VST2=0
)

target_link_libraries(TizWildinHub PRIVATE
  juce::juce_audio_utils
)
