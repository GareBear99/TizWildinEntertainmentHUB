#include "HubSettings.h"

namespace tiz
{

juce::PropertiesFile::Options HubSettings::makeOptions()
{
    juce::PropertiesFile::Options opts;
    opts.applicationName     = "TizWildinEntertainmentHUB";
    opts.filenameSuffix       = ".settings";
    opts.osxLibrarySubFolder  = "Application Support/TizWildinEntertainmentHUB";
    opts.folderName           = "TizWildinEntertainmentHUB";
    opts.storageFormat        = juce::PropertiesFile::storeAsXML;
    return opts;
}

HubSettings::HubSettings()
    : props (std::make_unique<juce::PropertiesFile> (makeOptions()))
{
}

// ── Auto-update ──────────────────────────────────────────────────────────────

bool HubSettings::getAutoUpdate() const
{
    return props->getBoolValue ("autoUpdate", true);
}

void HubSettings::setAutoUpdate (bool on)
{
    props->setValue ("autoUpdate", on);
    props->saveIfNeeded();
}

// ── Install root ─────────────────────────────────────────────────────────────

juce::File HubSettings::defaultInstallRoot()
{
#if JUCE_MAC
    return juce::File::getSpecialLocation (juce::File::userHomeDirectory)
               .getChildFile ("Library/Audio/Plug-Ins");
#elif JUCE_WINDOWS
    return juce::File ("C:\\Program Files\\Common Files\\VST3");
#else
    return juce::File::getSpecialLocation (juce::File::userHomeDirectory)
               .getChildFile (".vst3");
#endif
}

juce::File HubSettings::getInstallRoot() const
{
    auto stored = props->getValue ("installRoot", "");
    return stored.isNotEmpty() ? juce::File (stored) : defaultInstallRoot();
}

void HubSettings::setInstallRoot (const juce::File& dir)
{
    props->setValue ("installRoot", dir.getFullPathName());
    props->saveIfNeeded();
}

// ── Installed versions ───────────────────────────────────────────────────────

juce::String HubSettings::getInstalledVersion (const juce::String& pluginId) const
{
    return props->getValue ("installed_" + pluginId, "");
}

void HubSettings::setInstalledVersion (const juce::String& pluginId, const juce::String& versionTag)
{
    props->setValue ("installed_" + pluginId, versionTag);
    props->saveIfNeeded();
}

bool HubSettings::isInstalled (const juce::String& pluginId) const
{
    return getInstalledVersion (pluginId).isNotEmpty();
}

} // namespace tiz
