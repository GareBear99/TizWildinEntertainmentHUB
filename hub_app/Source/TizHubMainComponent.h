#pragma once
#include <JuceHeader.h>
#include "PluginManifest.h"
#include "GitHubClient.h"
#include "HubSettings.h"

// ── Per-plugin card ──────────────────────────────────────────────────────────
class PluginCard : public juce::Component
{
public:
    enum class State { unchecked, checking, hasRelease, sourceOnly, installed, updateAvailable, downloading, failed };

    PluginCard (const tiz::PluginInfo& plugin, tiz::HubSettings& settings);
    void paint (juce::Graphics& g) override;
    void resized() override;

    void setState (State s, const juce::String& versionText = {});
    State getState() const { return state; }
    const tiz::PluginInfo& getPlugin() const { return pluginInfo; }
    tiz::ReleaseInfo releaseInfo;

    std::function<void (PluginCard*)> onInstallClicked;

private:
    tiz::PluginInfo pluginInfo;
    tiz::HubSettings& settings;
    State state = State::unchecked;
    juce::String versionLabel;

    juce::TextButton actionButton;
    void updateActionButton();

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (PluginCard)
};

// ── Main component ───────────────────────────────────────────────────────────
class TizHubMainComponent : public juce::Component, private juce::Timer
{
public:
    TizHubMainComponent();
    ~TizHubMainComponent() override;

    void paint (juce::Graphics& g) override;
    void resized() override;

private:
    // ── colours (matching web dashboard) ──
    static constexpr juce::uint32 colBg         = 0xff0a0b12;
    static constexpr juce::uint32 colCard       = 0xff131222;
    static constexpr juce::uint32 colBorder     = 0xff1e2240;
    static constexpr juce::uint32 colAccent     = 0xff6c7bbd;
    static constexpr juce::uint32 colText       = 0xffe8eaf0;
    static constexpr juce::uint32 colSub        = 0xffa0a6bc;
    static constexpr juce::uint32 colGreen      = 0xff22c55e;

    tiz::GitHubClient github;
    tiz::HubSettings  settings;

    juce::Label titleLabel, subtitleLabel, statsLabel;
    juce::TextButton checkAllButton { "Check All Updates" };
    juce::TextButton installAllButton { "Install All" };
    juce::ToggleButton autoUpdateToggle { "Auto-check on launch" };

    juce::Viewport viewport;
    juce::Component scrollContent;
    juce::OwnedArray<juce::Label>     sectionLabels;
    juce::OwnedArray<PluginCard>      cards;

    juce::ThreadPool pool { 4 };

    void buildUI();
    void checkAllUpdates();
    void checkPlugin (PluginCard* card);
    void installPlugin (PluginCard* card);
    void installAll();
    void updateStats();

    void timerCallback() override;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (TizHubMainComponent)
};
