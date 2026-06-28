#include "PluginProcessor.h"
#include "PluginEditor.h"

TizWildinHubProcessor::TizWildinHubProcessor()
    : AudioProcessor (BusesProperties()
                        .withInput  ("Input",  juce::AudioChannelSet::stereo(), true)
                        .withOutput ("Output", juce::AudioChannelSet::stereo(), true))
{
}

void TizWildinHubProcessor::prepareToPlay (double /*sampleRate*/, int /*samplesPerBlock*/)
{
    // Nothing to prepare — passthrough only.
}

void TizWildinHubProcessor::releaseResources()
{
}

void TizWildinHubProcessor::processBlock (juce::AudioBuffer<float>& /*buffer*/,
                                          juce::MidiBuffer& /*midiMessages*/)
{
    // Pure passthrough — audio passes unchanged.
}

juce::AudioProcessorEditor* TizWildinHubProcessor::createEditor()
{
    return new TizWildinHubEditor (*this);
}

void TizWildinHubProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    // Save the Hub's account / last-action state so it persists with the DAW project.
    juce::XmlElement xml ("TizWildinHubState");
    // Future: persist accountId, last-viewed product, etc.
    copyXmlToBinary (xml, destData);
}

void TizWildinHubProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    if (auto xml = getXmlFromBinary (data, sizeInBytes))
    {
        if (xml->hasTagName ("TizWildinHubState"))
        {
            // Future: restore accountId, last-viewed product, etc.
        }
    }
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new TizWildinHubProcessor();
}
