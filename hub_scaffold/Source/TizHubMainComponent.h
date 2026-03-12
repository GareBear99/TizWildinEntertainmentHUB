#pragma once
#include <JuceHeader.h>
#include "TizHubState.h"

class TizHubMainComponent : public juce::Component,
                            private juce::Button::Listener
{
public:
    TizHubMainComponent();
    void resized() override;
    void paint(juce::Graphics& g) override;

private:
    void buttonClicked(juce::Button* button) override;
    void triggerRefresh();
    void triggerInstallMissing();
    void triggerCheckUpdates();

    TizHubState state;
    juce::TextButton refreshButton { "Refresh" };
    juce::TextButton installMissingButton { "Install Missing" };
    juce::TextButton checkUpdatesButton { "Check Updates" };
    juce::Label title;
};
