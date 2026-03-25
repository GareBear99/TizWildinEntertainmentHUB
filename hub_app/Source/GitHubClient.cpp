#include "GitHubClient.h"

namespace tiz
{

// ── JSON helper ──────────────────────────────────────────────────────────────
juce::var GitHubClient::getJson (const juce::URL& url) const
{
    auto options = juce::URL::InputStreamOptions (juce::URL::ParameterHandling::inAddress)
                       .withConnectionTimeoutMs (5000)
                       .withExtraHeaders ("Accept: application/vnd.github+json\r\n");

    if (auto stream = url.createInputStream (options))
        return juce::JSON::parse (stream->readEntireStreamAsString());

    return {};
}

// ── Platform asset matching ──────────────────────────────────────────────────
void GitHubClient::pickPlatformAsset (ReleaseInfo& info, const juce::var& assets)
{
    if (! assets.isArray())
        return;

    // Keywords we look for in asset file names per platform
#if JUCE_MAC
    const juce::StringArray keywords { "mac", "macos", "osx", "darwin", ".dmg" };
#elif JUCE_WINDOWS
    const juce::StringArray keywords { "win", "windows", ".zip", ".exe", ".msi" };
#else
    const juce::StringArray keywords { "linux", ".tar.gz", ".deb", ".AppImage" };
#endif

    for (const auto& asset : *assets.getArray())
    {
        auto name = asset.getProperty ("name", "").toString().toLowerCase();
        for (auto& kw : keywords)
        {
            if (name.contains (kw))
            {
                info.assetUrl  = asset.getProperty ("browser_download_url", "").toString();
                info.assetName = asset.getProperty ("name", "").toString();
                return;
            }
        }
    }
}

// ── Fetch latest release ─────────────────────────────────────────────────────
ReleaseInfo GitHubClient::fetchLatestRelease (const juce::String& repoName) const
{
    ReleaseInfo info;
    auto url = juce::URL ("https://api.github.com/repos/" + repoOwner + "/" + repoName + "/releases/latest");
    auto json = getJson (url);

    if (json.isVoid() || json.getProperty ("tag_name", "").toString().isEmpty())
        return info;   // 404 or parse failure → no release

    info.found       = true;
    info.tagName     = json.getProperty ("tag_name",     "").toString();
    info.htmlUrl     = json.getProperty ("html_url",     "").toString();
    info.publishedAt = json.getProperty ("published_at", "").toString();
    info.sourceZipUrl = json.getProperty ("zipball_url", "").toString();

    // Calculate days-ago
    auto published = juce::Time::fromISO8601 (info.publishedAt);
    if (published.toMilliseconds() > 0)
        info.daysAgo = static_cast<int> ((juce::Time::getCurrentTime() - published).inDays());

    // Try to find a platform-specific asset
    pickPlatformAsset (info, json.getProperty ("assets", {}));

    return info;
}

// ── Download a file ──────────────────────────────────────────────────────────
bool GitHubClient::downloadFile (const juce::String& urlStr, const juce::File& destination) const
{
    auto url = juce::URL (urlStr);
    auto options = juce::URL::InputStreamOptions (juce::URL::ParameterHandling::inAddress)
                       .withConnectionTimeoutMs (15000);

    if (auto stream = url.createInputStream (options))
    {
        juce::FileOutputStream out (destination);
        if (out.openedOk())
        {
            out.writeFromInputStream (*stream, -1);
            out.flush();
            return true;
        }
    }
    return false;
}

} // namespace tiz
