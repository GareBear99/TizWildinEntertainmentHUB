#include "ArcClient.h"

juce::var ArcClient::requestJson(const juce::URL& url)
{
    auto options = juce::URL::InputStreamOptions(juce::URL::ParameterHandling::inAddress).withConnectionTimeoutMs(2500);
    std::unique_ptr<juce::InputStream> input(url.createInputStream(options));
    if (input == nullptr) return {};
    return juce::JSON::parse(input->readEntireStreamAsString());
}

juce::var ArcClient::postJson(const juce::String& path, const juce::var& body)
{
    auto payload = juce::JSON::toString(body);
    auto options = juce::URL::InputStreamOptions(juce::URL::ParameterHandling::inAddress)
        .withConnectionTimeoutMs(2500)
        .withExtraHeaders("Content-Type: application/json\r\n")
        .withHttpRequestCmd("POST");
    auto url = juce::URL(serviceBaseUrl + path).withPOSTData(payload);
    std::unique_ptr<juce::InputStream> input(url.createInputStream(options));
    if (input == nullptr) return {};
    return juce::JSON::parse(input->readEntireStreamAsString());
}

juce::var ArcClient::fetchCatalog() { return requestJson(juce::URL(serviceBaseUrl + "/catalog")); }
juce::var ArcClient::fetchEntitlements(const juce::String& accountId) { return requestJson(juce::URL(serviceBaseUrl + "/entitlements/" + accountId)); }
juce::var ArcClient::fetchSeats(const juce::String& accountId) { return requestJson(juce::URL(serviceBaseUrl + "/seats/" + accountId)); }
juce::var ArcClient::fetchAccountSummary(const juce::String& accountId) { return requestJson(juce::URL(serviceBaseUrl + "/account-summary/" + accountId)); }
juce::var ArcClient::fetchMachines(const juce::String& accountId) { return requestJson(juce::URL(serviceBaseUrl + "/machines/" + accountId)); }
juce::var ArcClient::fetchReceipts(const juce::String& accountId) { return requestJson(juce::URL(serviceBaseUrl + "/receipts/" + accountId)); }
juce::var ArcClient::fetchReleases(const juce::String& productId) { return requestJson(juce::URL(serviceBaseUrl + "/releases" + (productId.isNotEmpty() ? ("?product_id=" + productId) : ""))); }
juce::var ArcClient::fetchSettings(const juce::String& accountId) { return requestJson(juce::URL(serviceBaseUrl + "/settings/" + accountId)); }
juce::var ArcClient::fetchActivity(const juce::String& accountId, int limit) { return requestJson(juce::URL(serviceBaseUrl + "/activity/" + accountId + "?limit=" + juce::String(limit))); }
juce::var ArcClient::fetchReadiness(const juce::String& accountId, const juce::String& machineId, const juce::String& channel) { return requestJson(juce::URL(serviceBaseUrl + "/readiness/" + accountId + (machineId.isNotEmpty() ? ("?machine_id=" + machineId) : "") + (channel.isNotEmpty() ? ((machineId.isNotEmpty() ? "&" : "?") + juce::String("channel=") + channel) : ""))); }
juce::var ArcClient::fetchAudit(const juce::String& accountId, const juce::String& machineId, const juce::String& channel) { return requestJson(juce::URL(serviceBaseUrl + "/audit/" + accountId + (machineId.isNotEmpty() ? ("?machine_id=" + machineId) : "") + (channel.isNotEmpty() ? ((machineId.isNotEmpty() ? "&" : "?") + juce::String("channel=") + channel) : ""))); }
juce::var ArcClient::fetchSupportBundle(const juce::String& accountId, const juce::String& machineId, const juce::String& channel) { return requestJson(juce::URL(serviceBaseUrl + "/support/bundle/" + accountId + (machineId.isNotEmpty() ? ("?machine_id=" + machineId) : "") + (channel.isNotEmpty() ? ((machineId.isNotEmpty() ? "&" : "?") + juce::String("channel=") + channel) : ""))); }
juce::var ArcClient::postProposal(const juce::var& body) { return postJson("/proposal", body); }
juce::var ArcClient::postInstallScan(const juce::var& body) { return postJson("/install-scan", body); }
juce::var ArcClient::postInstallPlan(const juce::var& body) { return postJson("/install-plan", body); }
juce::var ArcClient::postDownloadPlan(const juce::var& body) { return postJson("/download-plan", body); }
juce::var ArcClient::postSeatRelease(const juce::var& body) { return postJson("/seats/release", body); }
juce::var ArcClient::postSettings(const juce::var& body) { return postJson("/settings", body); }
juce::var ArcClient::exportDiagnostics(const juce::String& accountId) { return requestJson(juce::URL(serviceBaseUrl + "/diagnostics/export/" + accountId)); }
juce::var ArcClient::exportBackup(const juce::String& tag) { return postJson("/backups/export" + (tag.isNotEmpty() ? ("?tag=" + tag) : ""), juce::var(new juce::DynamicObject())); }
juce::var ArcClient::fetchBackups() { return requestJson(juce::URL(serviceBaseUrl + "/backups")); }
juce::var ArcClient::postExecuteDownloads(const juce::var& body) { return postJson("/execute-downloads", body); }
juce::var ArcClient::postPreflight(const juce::var& body) { return postJson("/preflight", body); }
juce::var ArcClient::postSync(const juce::var& body) { return postJson("/sync", body); }
juce::var ArcClient::postStageLocal(const juce::String& channel) { return postJson("/releases/stage-local" + (channel.isNotEmpty() ? ("?channel=" + channel) : ""), juce::var(new juce::DynamicObject())); }
juce::var ArcClient::fetchLaunchpad(const juce::String& accountId, const juce::String& machineId, const juce::String& channel) { return requestJson(juce::URL(serviceBaseUrl + "/launchpad/" + accountId + "?machine_id=" + machineId + (channel.isNotEmpty() ? ("&channel=" + channel) : ""))); }
juce::var ArcClient::postDemoBootstrap(bool stageArtifacts) { return postJson("/demo/bootstrap?stage_artifacts=" + juce::String(stageArtifacts ? "true" : "false"), juce::var(new juce::DynamicObject())); }
