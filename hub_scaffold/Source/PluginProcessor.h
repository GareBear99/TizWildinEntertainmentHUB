#pragma once
#include <JuceHeader.h>

/**
 * TizWildinHub audio processor — passthrough only.
 *
 * This plugin performs zero DSP.  Its only purpose is to provide a
 * VST3 / AU entry point so the Hub UI appears in DAW plugin lists
 * under "TizWildin Entertainment", right alongside FreeEQ8 and the
 * rest of the catalog.
 */
class TizWildinHubProcessor final : public juce::AudioProcessor
{
public:
    TizWildinHubProcessor();
    ~TizWildinHubProcessor() override = default;

    // --- AudioProcessor overrides ---
    void prepareToPlay (double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;
    void processBlock (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }

    const juce::String getName() const override { return JucePlugin_Name; }

    bool acceptsMidi()  const override { return false; }
    bool producesMidi() const override { return false; }
    bool isMidiEffect() const override { return false; }
    double getTailLengthSeconds() const override { return 0.0; }

    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram (int) override {}
    const juce::String getProgramName (int) override { return {}; }
    void changeProgramName (int, const juce::String&) override {}

    void getStateInformation (juce::MemoryBlock& destData) override;
    void setStateInformation (const void* data, int sizeInBytes) override;

private:
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (TizWildinHubProcessor)
};
