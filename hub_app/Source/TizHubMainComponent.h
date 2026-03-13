#pragma once
#include <JuceHeader.h>
#include "ArcClient.h"

class TizHubMainComponent : public juce::Component, private juce::Button::Listener
{
public:
    TizHubMainComponent();
    void paint(juce::Graphics& g) override;
    void resized() override;
private:
    void buttonClicked(juce::Button* button) override;
    void refreshAll();
    void rebuildCards(const juce::var& catalog, const juce::var& entitlements);
    ArcClient arcClient { "http://127.0.0.1:8000" };
    juce::String activeAccountId { "demo_account" };
    juce::Label title, subtitle, summaryLabel, statusLabel, seatLabel, settingsLabel, machineLabel;
    juce::String activeMachineId { "hub_desktop" };
    juce::TextButton refreshButton { "Refresh" }, bootstrapButton { "Bootstrap Demo" }, installPlanButton { "Plan Installs" }, executeButton { "Execute" }, stageButton { "Stage Artifacts" }, preflightButton { "Preflight" }, backupButton { "Backup State" }, releaseSeatButton { "Release First Seat" }, exportDiagnosticsButton { "Export Diagnostics" };
    juce::Viewport cardsViewport;
    juce::Component cardsContainer;
    juce::OwnedArray<juce::Component> cardComponents;
};
