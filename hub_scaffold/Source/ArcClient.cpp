#include "ArcClient.h"

static juce::var requestJson(const juce::URL& url)
{
    auto input = url.createInputStream(false);
    if (input == nullptr)
        return {};
    return juce::JSON::parse(input->readEntireStreamAsString());
}

juce::var ArcClient::fetchCatalog()
{
    return requestJson(juce::URL(serviceBaseUrl + "/catalog"));
}

juce::var ArcClient::fetchEntitlements(const juce::String& accountId)
{
    return requestJson(juce::URL(serviceBaseUrl + "/entitlements/" + accountId));
}

juce::var ArcClient::postProposal(const juce::var&)
{
    return {};
}
