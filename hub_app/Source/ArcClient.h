#pragma once
#include <JuceHeader.h>

class ArcClient
{
public:
    explicit ArcClient(juce::String baseUrl) : serviceBaseUrl(std::move(baseUrl)) {}
    juce::var fetchCatalog();
    juce::var fetchEntitlements(const juce::String& accountId);
    juce::var fetchSeats(const juce::String& accountId);
    juce::var fetchAccountSummary(const juce::String& accountId);
    juce::var fetchMachines(const juce::String& accountId);
    juce::var fetchReceipts(const juce::String& accountId);
    juce::var fetchReleases(const juce::String& productId = {});
    juce::var fetchSettings(const juce::String& accountId);
    juce::var fetchActivity(const juce::String& accountId, int limit = 25);
    juce::var fetchReadiness(const juce::String& accountId, const juce::String& machineId = {}, const juce::String& channel = {});
    juce::var fetchAudit(const juce::String& accountId, const juce::String& machineId = {}, const juce::String& channel = {});
    juce::var fetchSupportBundle(const juce::String& accountId, const juce::String& machineId = {}, const juce::String& channel = {});
    juce::var exportDiagnostics(const juce::String& accountId);
    juce::var exportBackup(const juce::String& tag = {});
    juce::var fetchBackups();
    juce::var fetchLaunchpad(const juce::String& accountId, const juce::String& machineId, const juce::String& channel = {});
    juce::var postExecuteDownloads(const juce::var& body);
    juce::var postPreflight(const juce::var& body);
    juce::var postSync(const juce::var& body);
    juce::var postStageLocal(const juce::String& channel = {});
    juce::var postProposal(const juce::var& body);
    juce::var postInstallScan(const juce::var& body);
    juce::var postInstallPlan(const juce::var& body);
    juce::var postDownloadPlan(const juce::var& body);
    juce::var postSeatRelease(const juce::var& body);
    juce::var postSettings(const juce::var& body);
    juce::var postDemoBootstrap(bool stageArtifacts = true);
private:
    juce::String serviceBaseUrl;
    juce::var requestJson(const juce::URL& url);
    juce::var postJson(const juce::String& path, const juce::var& body);
};
