#pragma once
#include <JuceHeader.h>
#include "PluginProcessor.h"
#include "TizHubMainComponent.h"

class TizWildinHubEditor final : public juce::AudioProcessorEditor
{
public:
    explicit TizWildinHubEditor (TizWildinHubProcessor& p)
        : AudioProcessorEditor (&p), processor (p)
    {
        addAndMakeVisible (hubComponent);
        setResizable (true, true);
        setSize (1280, 820);
    }

    void resized() override
    {
        hubComponent.setBounds (getLocalBounds());
    }

private:
    TizWildinHubProcessor& processor;
    TizHubMainComponent hubComponent;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (TizWildinHubEditor)
};
