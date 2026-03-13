#include "TizHubMainComponent.h"

namespace
{
class ProductCard : public juce::Component
{
public:
    ProductCard(juce::String t, juce::String s, juce::String b) : title(std::move(t)), subtitle(std::move(s)), badge(std::move(b)) {}
    void paint(juce::Graphics& g) override
    {
        auto r = getLocalBounds().toFloat();
        g.setColour(juce::Colour::fromRGB(19, 22, 34));
        g.fillRoundedRectangle(r, 12.0f);
        g.setColour(juce::Colour::fromRGB(46, 56, 84));
        g.drawRoundedRectangle(r.reduced(0.5f), 12.0f, 1.0f);
        g.setColour(juce::Colours::white);
        g.setFont(18.0f);
        g.drawText(title, getLocalBounds().removeFromTop(34).reduced(14, 10), juce::Justification::centredLeft);
        g.setFont(13.0f);
        g.setColour(juce::Colour::fromRGB(185, 190, 205));
        g.drawText(subtitle, getLocalBounds().reduced(14).withTop(42).removeFromTop(34), juce::Justification::centredLeft, true);
        auto badgeArea = getLocalBounds().reduced(14).removeFromBottom(30).removeFromLeft(180).toFloat();
        g.setColour(juce::Colour::fromRGB(88, 104, 176));
        g.fillRoundedRectangle(badgeArea, 8.0f);
        g.setColour(juce::Colours::white);
        g.setFont(12.0f);
        g.drawFittedText(badge, badgeArea.toNearestInt(), juce::Justification::centred, 1);
    }
private:
    juce::String title, subtitle, badge;
};
}

TizHubMainComponent::TizHubMainComponent()
{
    title.setText("TizWildin Entertainment HUB", juce::dontSendNotification);
    title.setFont(juce::FontOptions(28.0f, juce::Font::bold));
    subtitle.setText("ARC-backed control surface for products, staging, preflight, installs, backups, seats, and diagnostics.", juce::dontSendNotification);
    subtitle.setColour(juce::Label::textColourId, juce::Colour::fromRGB(170, 176, 193));
    summaryLabel.setJustificationType(juce::Justification::centredLeft);
    seatLabel.setJustificationType(juce::Justification::topLeft);
    settingsLabel.setJustificationType(juce::Justification::topLeft);
    settingsLabel.setText("Settings\n- ARC endpoint: localhost\n- Account: demo_account\n- Mode: operator scaffold\n- Channel: stable", juce::dontSendNotification);
    machineLabel.setJustificationType(juce::Justification::topLeft);
    for (auto* c : { &title, &subtitle, &summaryLabel, &statusLabel, &seatLabel, &settingsLabel, &machineLabel, &refreshButton, &bootstrapButton, &installPlanButton, &executeButton, &stageButton, &preflightButton, &backupButton, &releaseSeatButton, &exportDiagnosticsButton }) addAndMakeVisible(*c);
    for (auto* b : { &refreshButton, &bootstrapButton, &installPlanButton, &executeButton, &stageButton, &preflightButton, &backupButton, &releaseSeatButton, &exportDiagnosticsButton }) b->addListener(this);
    cardsViewport.setViewedComponent(&cardsContainer, false);
    addAndMakeVisible(cardsViewport);
    refreshAll();
}

void TizHubMainComponent::paint(juce::Graphics& g) { g.fillAll(juce::Colour::fromRGB(10, 11, 18)); }

void TizHubMainComponent::resized()
{
    auto area = getLocalBounds().reduced(18);
    auto header = area.removeFromTop(76);
    title.setBounds(header.removeFromTop(36));
    subtitle.setBounds(header);
    auto topRow = area.removeFromTop(54);
    summaryLabel.setBounds(topRow.removeFromLeft(360));
    refreshButton.setBounds(topRow.removeFromLeft(94).reduced(4));
    bootstrapButton.setBounds(topRow.removeFromLeft(120).reduced(4));
    installPlanButton.setBounds(topRow.removeFromLeft(110).reduced(4));
    stageButton.setBounds(topRow.removeFromLeft(120).reduced(4));
    preflightButton.setBounds(topRow.removeFromLeft(100).reduced(4));
    executeButton.setBounds(topRow.removeFromLeft(90).reduced(4));
    backupButton.setBounds(topRow.removeFromLeft(110).reduced(4));
    releaseSeatButton.setBounds(topRow.removeFromLeft(140).reduced(4));
    exportDiagnosticsButton.setBounds(topRow.removeFromLeft(150).reduced(4));
    statusLabel.setBounds(area.removeFromTop(28));
    auto right = area.removeFromRight(320);
    seatLabel.setBounds(right.removeFromTop(180));
    machineLabel.setBounds(right.removeFromTop(180));
    settingsLabel.setBounds(right.reduced(0, 8));
    cardsViewport.setBounds(area);
    cardsContainer.setSize(cardsViewport.getWidth() - 12, juce::jmax(400, 14 + cardComponents.size() * 126));
    int y = 8;
    for (auto* c : cardComponents) { c->setBounds(8, y, cardsContainer.getWidth() - 16, 112); y += 122; }
}

void TizHubMainComponent::buttonClicked(juce::Button* button)
{
    auto makeRequestBody = [this]() {
        juce::DynamicObject::Ptr body = new juce::DynamicObject();
        body->setProperty("accountId", activeAccountId);
        body->setProperty("machineId", activeMachineId);
        body->setProperty("requestedProducts", juce::Array<juce::var>{ "freeeq8", "therum", "paintmask" });
        body->setProperty("channel", "stable");
        return body;
    };
    if (button == &refreshButton) { refreshAll(); return; }
    if (button == &bootstrapButton)
    {
        auto reply = arcClient.postDemoBootstrap(true);
        statusLabel.setText(reply.getProperty("approved", false) ? "Demo state bootstrapped" : "Demo bootstrap failed", juce::dontSendNotification);
        refreshAll();
        return;
    }
    if (button == &installPlanButton)
    {
        auto reply = arcClient.postInstallPlan(juce::var(makeRequestBody().get()));
        auto actions = reply.getProperty("actions", juce::var());
        auto count = actions.isArray() ? actions.getArray()->size() : 0;
        statusLabel.setText(reply.isVoid() ? "Install plan failed" : ("Install plan ready: " + juce::String(count) + " actions"), juce::dontSendNotification);
        return;
    }
    if (button == &stageButton)
    {
        auto reply = arcClient.postStageLocal("stable");
        auto staged = reply.getProperty("staged", juce::var());
        auto count = staged.isArray() ? staged.getArray()->size() : 0;
        statusLabel.setText(reply.isVoid() ? "Stage failed" : ("Artifacts staged: " + juce::String(count)), juce::dontSendNotification);
        return;
    }
    if (button == &preflightButton)
    {
        auto reply = arcClient.postPreflight(juce::var(makeRequestBody().get()));
        auto warnings = reply.getProperty("warnings", juce::var());
        auto count = warnings.isArray() ? warnings.getArray()->size() : 0;
        statusLabel.setText(reply.isVoid() ? "Preflight failed" : ("Preflight complete: " + juce::String(count) + " warning(s)"), juce::dontSendNotification);
        return;
    }
    if (button == &executeButton)
    {
        auto body = makeRequestBody();
        body->setProperty("dryRun", false);
        body->setProperty("installRoot", "/tmp/tizhub_installs");
        auto reply = arcClient.postExecuteDownloads(juce::var(body.get()));
        auto executed = reply.getProperty("executed", juce::var());
        auto count = executed.isArray() ? executed.getArray()->size() : 0;
        statusLabel.setText(reply.isVoid() ? "Execute failed" : ("Executed: " + juce::String(count)), juce::dontSendNotification);
        refreshAll();
        return;
    }
    if (button == &backupButton)
    {
        auto reply = arcClient.exportBackup("hub_ui");
        auto path = reply.getProperty("path", "").toString();
        statusLabel.setText(path.isNotEmpty() ? ("Backup written: " + path) : "Backup failed", juce::dontSendNotification);
        return;
    }
    if (button == &exportDiagnosticsButton)
    {
        auto reply = arcClient.exportDiagnostics(activeAccountId);
        auto path = reply.getProperty("path", "").toString();
        statusLabel.setText(path.isNotEmpty() ? ("Diagnostics exported: " + path) : "Diagnostics export failed", juce::dontSendNotification);
        return;
    }
    if (button == &releaseSeatButton)
    {
        auto seats = arcClient.fetchSeats(activeAccountId);
        if (auto* arr = seats.getArray(); arr != nullptr && !arr->isEmpty())
        {
            auto first = arr->getReference(0);
            juce::DynamicObject::Ptr body = new juce::DynamicObject();
            body->setProperty("accountId", activeAccountId);
            body->setProperty("seatId", first.getProperty("seatId", ""));
            auto reply = arcClient.postSeatRelease(juce::var(body.get()));
            statusLabel.setText(reply.isVoid() ? "Seat release failed" : "Seat released", juce::dontSendNotification);
            refreshAll();
            return;
        }
        statusLabel.setText("No seats to release", juce::dontSendNotification);
    }
}

void TizHubMainComponent::refreshAll()
{
    auto launchpad = arcClient.fetchLaunchpad(activeAccountId, activeMachineId, "stable");
    auto summary = arcClient.fetchAccountSummary(activeAccountId);
    auto catalog = arcClient.fetchCatalog();
    auto entitlements = arcClient.fetchEntitlements(activeAccountId);
    auto machines = arcClient.fetchMachines(activeAccountId);
    auto backups = arcClient.fetchBackups();
    auto settings = arcClient.fetchSettings(activeAccountId);
    auto readiness = arcClient.fetchReadiness(activeAccountId, activeMachineId, "stable");
    auto activity = arcClient.fetchActivity(activeAccountId, 5);
    if (summary.isVoid() || catalog.isVoid() || entitlements.isVoid() || machines.isVoid())
    {
        statusLabel.setText("Could not reach ARC at http://127.0.0.1:8000", juce::dontSendNotification);
        summaryLabel.setText("Account: demo_account | ARC offline", juce::dontSendNotification);
        seatLabel.setText("Seats\n- unavailable", juce::dontSendNotification);
        machineLabel.setText("Machines\n- unavailable", juce::dontSendNotification);
        return;
    }
    auto stats = summary.getProperty("stats", juce::var());
    auto backupCount = backups.getProperty("backups", juce::var()).isArray() ? backups.getProperty("backups", juce::var()).getArray()->size() : 0;
    auto overview = launchpad.getProperty("overview", juce::var());
    auto readyText = readiness.getProperty("ready", false) ? "READY" : "BLOCKED";
    summaryLabel.setText("Account: " + activeAccountId + " | " + readyText + " | Seats: " + juce::String((int) stats.getProperty("activeSeatCount", 0)) + "/" + juce::String((int) stats.getProperty("maxSeats", 0)) + " | Installable: " + juce::String((int) overview.getProperty("installableCount", 0)) + " | Updates: " + juce::String((int) overview.getProperty("pendingUpdateCount", 0)) + " | Backups: " + juce::String(backupCount), juce::dontSendNotification);
    auto seatText = juce::String("Seats\n");
    if (auto* arr = summary.getProperty("seats", juce::var()).getArray())
        for (const auto& s : *arr)
            seatText += "- " + s.getProperty("machineId", "") .toString() + " • " + s.getProperty("productId", "") .toString() + " • " + s.getProperty("status", "") .toString() + "\n";
    seatLabel.setText(seatText, juce::dontSendNotification);
    auto machineText = juce::String("Machines\n");
    if (auto* marr = machines.getProperty("machines", juce::var()).getArray())
        for (const auto& m : *marr)
            machineText += "- " + m.getProperty("machineId", "").toString() + " • products: " + juce::String((int) m.getProperty("productCount", 0)) + "\n";
    machineLabel.setText(machineText, juce::dontSendNotification);
    auto activityText = juce::String();
    if (auto* items = activity.getProperty("items", juce::var()).getArray())
        for (const auto& item : *items)
            activityText += "\n- " + item.getProperty("summary", "").toString();
    settingsLabel.setText("Settings\n- ARC: " + settings.getProperty("arcBaseUrl", "http://127.0.0.1:8000").toString() + "\n- Channel: " + settings.getProperty("preferredChannel", "stable").toString() + "\n- Theme: " + settings.getProperty("theme", "dark").toString() + "\n- Install root: " + settings.getProperty("installRoot", "/tmp/tizhub_installs").toString() + "\n- Auto backup: " + (bool(settings.getProperty("autoBackupBeforeExecute", true)) ? juce::String("on") : juce::String("off")) + "\nRecent activity" + activityText, juce::dontSendNotification);
    statusLabel.setText("ARC summary refreshed", juce::dontSendNotification);
    rebuildCards(catalog, entitlements);
}

void TizHubMainComponent::rebuildCards(const juce::var& catalog, const juce::var& entitlements)
{
    cardComponents.clear(true);
    cardsContainer.removeAllChildren();
    auto* products = catalog.getProperty("products", juce::var()).getArray();
    juce::StringArray owned;
    if (auto* ownedArray = entitlements.getProperty("ownedProducts", juce::var()).getArray()) for (const auto& item : *ownedArray) owned.add(item.toString());
    bool complete = (bool) entitlements.getProperty("ownsEveryVST", false);
    if (products != nullptr)
        for (const auto& p : *products)
        {
            auto productId = p.getProperty("productId", "").toString();
            auto name = p.getProperty("displayName", "").toString();
            auto status = p.getProperty("status", "unknown").toString();
            auto licenseClass = p.getProperty("licenseClass", "").toString();
            juce::String badge = licenseClass.startsWith("FREE") ? "FREE" : (complete || owned.contains(productId) ? "OWNED" : "LOCKED");
            auto* card = new ProductCard(name, productId + " • " + status + " • " + licenseClass, badge);
            cardComponents.add(card);
            cardsContainer.addAndMakeVisible(card);
        }
    resized();
}
