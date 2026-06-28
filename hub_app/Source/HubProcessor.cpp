#include "HubProcessor.h"
#include "HubEditor.h"

HubProcessor::HubProcessor()
    : AudioProcessor (BusesProperties()
                          .withInput  ("Input",  juce::AudioChannelSet::stereo(), true)
                          .withOutput ("Output", juce::AudioChannelSet::stereo(), true))
{
}

juce::AudioProcessorEditor* HubProcessor::createEditor()
{
    return new HubEditor (*this);
}

// This creates the plugin instances when loaded by a host
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new HubProcessor();
}
