#pragma once
#include <JuceHeader.h>
#include "HubProcessor.h"
#include "TizHubMainComponent.h"

/**
 *  Plugin editor — wraps TizHubMainComponent as the in-DAW UI.
 *  When loaded in Ableton/Logic/Reaper the user sees the full HUB
 *  with plugin cards, install buttons, and version checking.
 */
class HubEditor final : public juce::AudioProcessorEditor
{
public:
    explicit HubEditor (HubProcessor& p)
        : AudioProcessorEditor (p)
    {
        addAndMakeVisible (mainComponent);
        setSize (1100, 780);
        setResizable (true, true);
        setResizeLimits (800, 500, 1800, 1200);
    }

    void resized() override
    {
        mainComponent.setBounds (getLocalBounds());
    }

private:
    TizHubMainComponent mainComponent;
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (HubEditor)
};
