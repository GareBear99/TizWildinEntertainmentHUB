#include "TizHubMainComponent.h"

TizHubMainComponent::TizHubMainComponent()
{
    title.setText("TizWildin Hub", juce::dontSendNotification);
    title.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(title);

    for (auto* b : { &refreshButton, &installMissingButton, &checkUpdatesButton })
    {
        b->addListener(this);
        addAndMakeVisible(*b);
    }
}

void TizHubMainComponent::paint(juce::Graphics& g)
{
    g.fillAll(juce::Colour::fromRGB(10, 11, 18));
}

void TizHubMainComponent::resized()
{
    auto area = getLocalBounds().reduced(16);
    auto top = area.removeFromTop(40);
    title.setBounds(top.removeFromLeft(320));
    refreshButton.setBounds(top.removeFromLeft(120));
    top.removeFromLeft(8);
    installMissingButton.setBounds(top.removeFromLeft(150));
    top.removeFromLeft(8);
    checkUpdatesButton.setBounds(top.removeFromLeft(150));
}

void TizHubMainComponent::buttonClicked(juce::Button* button)
{
    if (button == &refreshButton) triggerRefresh();
    if (button == &installMissingButton) triggerInstallMissing();
    if (button == &checkUpdatesButton) triggerCheckUpdates();
}

void TizHubMainComponent::triggerRefresh()      { state.lastAction = "refresh"; }
void TizHubMainComponent::triggerInstallMissing(){ state.lastAction = "install_missing"; }
void TizHubMainComponent::triggerCheckUpdates() { state.lastAction = "check_updates"; }
