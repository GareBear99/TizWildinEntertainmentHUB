#pragma once
#include <JuceHeader.h>

class TizHubApplication final : public juce::JUCEApplication
{
public:
    const juce::String getApplicationName() override      { return "TizWildin Hub"; }
    const juce::String getApplicationVersion() override   { return "0.1.0"; }
    bool moreThanOneInstanceAllowed() override            { return true; }

    void initialise (const juce::String&) override;
    void shutdown() override;

private:
    std::unique_ptr<juce::DocumentWindow> mainWindow;
};
