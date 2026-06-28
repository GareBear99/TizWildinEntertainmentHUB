#pragma once
#include <JuceHeader.h>

namespace tiz
{

struct PluginInfo
{
    juce::String id;
    juce::String name;
    juce::String description;
    juce::String category;      // "flagship", "instruments", "maid_suite", "sound_design", "experimental"
    juce::String repo;
    juce::StringArray formats;  // "VST3", "AU", "Standalone"
    juce::String status;        // "production", "beta", "dev"
};

struct Category
{
    juce::String id;
    juce::String name;
    juce::String icon;
};

inline const juce::Array<Category>& getCategories()
{
    static const juce::Array<Category> cats = {
        { "flagship",      "Flagship",                   "F" },
        { "instruments",   "Instruments",                "I" },
        { "maid_suite",    "Maid Suite",                 "M" },
        { "sound_design",  "Sound Design",               "S" },
        { "experimental",  "Experimental",               "E" }
    };
    return cats;
}

inline const juce::Array<PluginInfo>& getAllPlugins()
{
    static const juce::Array<PluginInfo> plugins = {
        { "freeeq8",       "FreeEQ8",
          "8-band parametric EQ — dynamic EQ, linear phase, match EQ, M/S, spectrum analyzer.",
          "flagship",      "FreeEQ8",
          { "VST3", "AU", "Standalone" }, "production" },

        { "paintmask",     "PaintMask",
          "Visual paint-based audio processing — brush strokes become MIDI patterns.",
          "flagship",      "PaintMask_Free-JUCE-Plugin",
          { "VST3", "AU" },               "production" },

        { "wurp",          "WURP",
          "Toxic Motion Engine — formant motion, corrosive saturation, elastic pitch.",
          "flagship",      "WURP_Toxic-Motion-Engine_JUCE",
          { "VST3", "AU" },               "production" },

        { "aether",        "AETHER",
          "Choir & atmosphere designer — procedural choirs, pads, evolving textures.",
          "flagship",      "AETHER_Choir-Atmosphere-Designer",
          { "VST3", "AU" },               "beta" },

        { "whispergate",   "WhisperGate",
          "Procedural whispers and ritual atmospheres via interactive geometry.",
          "flagship",      "WhisperGate_Free-JUCE-Plugin",
          { "VST3", "AU" },               "production" },

        { "therum",        "Therum",
          "Bootleg Serum — free wavetable synth with visual waveform editing.",
          "flagship",      "Therum_JUCE-Plugin",
          { "VST3", "AU" },               "production" },

        { "instrudio",     "Instrudio",
          "10 fully playable instruments — cross-platform instrument ecosystem.",
          "instruments",   "Instrudio",
          { "VST3", "AU", "Standalone" }, "beta" },

        { "bassmaid",      "BassMaid",
          "Bass enhancement and low-end processing toolkit.",
          "maid_suite",    "BassMaid",
          { "VST3", "AU" },               "production" },

        { "spacemaid",     "SpaceMaid",
          "Spatial audio — depth, width, and reverb tools.",
          "maid_suite",    "SpaceMaid",
          { "VST3", "AU" },               "production" },

        { "gluemaid",      "GlueMaid",
          "Mix bus glue and cohesion — compression and tonal shaping.",
          "maid_suite",    "GlueMaid",
          { "VST3", "AU" },               "production" },

        { "mixmaid",       "MixMaid",
          "Spectral balance and mix correction — guides mixes toward tonal balance.",
          "maid_suite",    "MixMaid",
          { "VST3", "AU" },               "production" },

        { "chainmaid",     "ChainMaid",
          "Sidechain ducking and pumping effects for EDM, trap, and mix engineering.",
          "maid_suite",    "ChainMaid",
          { "VST3", "AU" },               "production" },

        { "riftwavesuite", "RiftWave Suite",
          "Modular synth + waveform synthesis — RiftSynth + WaveForm.",
          "sound_design",  "RiftWaveSuite_RiftSynth_WaveForm_Lite",
          { "VST3", "AU" },               "beta" },

        { "freesampler",   "FreeSampler",
          "Lightweight high-performance audio sampler plugin.",
          "experimental",  "FreeSampler_v0.3",
          { "VST3", "AU" },               "dev" }
    };
    return plugins;
}

inline juce::Array<PluginInfo> getPluginsForCategory (const juce::String& catId)
{
    juce::Array<PluginInfo> result;
    for (auto& p : getAllPlugins())
        if (p.category == catId)
            result.add (p);
    return result;
}

} // namespace tiz
