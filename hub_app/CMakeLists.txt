cmake_minimum_required(VERSION 3.22)
project(TizWildinEntertainmentHUB VERSION 0.2.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(
  JUCE
  GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
  GIT_TAG 8.0.6
)
FetchContent_MakeAvailable(JUCE)

juce_add_gui_app(TizWildinEntertainmentHUB
  PRODUCT_NAME "TizWildin Entertainment HUB"
)

juce_generate_juce_header(TizWildinEntertainmentHUB)

target_sources(TizWildinEntertainmentHUB PRIVATE
  Source/Main.cpp
  Source/TizHubApplication.h
  Source/TizHubApplication.cpp
  Source/TizHubMainComponent.h
  Source/TizHubMainComponent.cpp
  Source/ArcClient.h
  Source/ArcClient.cpp
)

target_compile_definitions(TizWildinEntertainmentHUB PRIVATE
  JUCE_WEB_BROWSER=0
  JUCE_USE_CURL=0
)

target_link_libraries(TizWildinEntertainmentHUB PRIVATE
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
