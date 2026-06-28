cmake_minimum_required(VERSION 3.22)
project(TizWildinEntertainmentHUB VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(
  JUCE
  GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
  GIT_TAG 8.0.6
)
FetchContent_MakeAvailable(JUCE)

# Build as VST3 + AU + Standalone so it works inside DAWs (Ableton, Logic, Reaper)
# AND as a standalone desktop app.
juce_add_plugin(TizWildinEntertainmentHUB
  PRODUCT_NAME           "TizWildin Entertainment HUB"
  COMPANY_NAME           "TizWildin Entertainment"
  PLUGIN_MANUFACTURER_CODE TzWd
  PLUGIN_CODE            TzHb
  FORMATS                VST3 AU Standalone
  IS_SYNTH               FALSE
  NEEDS_MIDI_INPUT       FALSE
  NEEDS_MIDI_OUTPUT      FALSE
  IS_MIDI_EFFECT         FALSE
  EDITOR_WANTS_KEYBOARD_FOCUS TRUE
  COPY_PLUGIN_AFTER_BUILD TRUE
)

juce_generate_juce_header(TizWildinEntertainmentHUB)

target_sources(TizWildinEntertainmentHUB PRIVATE
  Source/HubProcessor.h
  Source/HubProcessor.cpp
  Source/HubEditor.h
  Source/TizHubMainComponent.h
  Source/TizHubMainComponent.cpp
  Source/PluginManifest.h
  Source/GitHubClient.h
  Source/GitHubClient.cpp
  Source/HubSettings.h
  Source/HubSettings.cpp
)

target_compile_definitions(TizWildinEntertainmentHUB PRIVATE
  JUCE_WEB_BROWSER=0
  JUCE_USE_CURL=1
  JUCE_VST3_CAN_REPLACE_VST2=0
)

target_link_libraries(TizWildinEntertainmentHUB PRIVATE
  juce::juce_audio_basics
  juce::juce_audio_processors
  juce::juce_audio_utils
  juce::juce_gui_extra
  juce::juce_gui_basics
  juce::juce_graphics
  juce::juce_events
  juce::juce_core
  juce::juce_data_structures
  juce::juce_cryptography
  juce::juce_recommended_config_flags
  juce::juce_recommended_lto_flags
  juce::juce_recommended_warning_flags
)
