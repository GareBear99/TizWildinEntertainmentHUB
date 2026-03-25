#pragma once
#include <JuceHeader.h>

namespace tiz
{

/**
 *  Persists user preferences in a platform-appropriate config directory.
 *  - Auto-update toggle
 *  - Install root override
 *  - Installed plugin versions map  (pluginId → versionTag)
 */
class HubSettings
{
public:
    HubSettings();

    // ── Auto-update ──
    bool getAutoUpdate() const;
    void setAutoUpdate (bool on);

    // ── Install root ──
    juce::File getInstallRoot() const;
    void setInstallRoot (const juce::File& dir);

    /** Default install root for the current OS. */
    static juce::File defaultInstallRoot();

    // ── Installed versions ──
    juce::String getInstalledVersion (const juce::String& pluginId) const;
    void setInstalledVersion (const juce::String& pluginId, const juce::String& versionTag);
    bool isInstalled (const juce::String& pluginId) const;

private:
    std::unique_ptr<juce::PropertiesFile> props;

    static juce::PropertiesFile::Options makeOptions();
};

} // namespace tiz
