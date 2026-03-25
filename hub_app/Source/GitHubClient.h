#pragma once
#include <JuceHeader.h>

namespace tiz
{

/** Lightweight info about a GitHub release. */
struct ReleaseInfo
{
    bool found = false;
    juce::String tagName;
    juce::String htmlUrl;
    juce::String publishedAt;
    int daysAgo = -1;

    /** Platform-specific asset download URL (empty if no matching asset). */
    juce::String assetUrl;
    juce::String assetName;

    /** Source-code zip fallback. */
    juce::String sourceZipUrl;
};

/**
 *  Talks directly to the public GitHub REST API (no auth required, 60 req/hr).
 *  All network calls are synchronous — call them from a background thread.
 */
class GitHubClient
{
public:
    explicit GitHubClient (const juce::String& owner = "GareBear99")
        : repoOwner (owner) {}

    /** Fetch the latest release for a given repo name. */
    ReleaseInfo fetchLatestRelease (const juce::String& repoName) const;

    /** Download a URL to a local file. Returns true on success. */
    bool downloadFile (const juce::String& url, const juce::File& destination) const;

private:
    juce::String repoOwner;
    juce::var getJson (const juce::URL& url) const;

    /** Pick the best asset for the current platform from a release's asset list. */
    static void pickPlatformAsset (ReleaseInfo& info, const juce::var& assets);
};

} // namespace tiz
