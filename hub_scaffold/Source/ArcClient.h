#pragma once
#include <JuceHeader.h>

class ArcClient
{
public:
    explicit ArcClient(juce::String baseUrl) : serviceBaseUrl(std::move(baseUrl)) {}

    juce::var fetchCatalog();
    juce::var fetchEntitlements(const juce::String& accountId);
    juce::var postProposal(const juce::var& body);

private:
    juce::String serviceBaseUrl;
};
