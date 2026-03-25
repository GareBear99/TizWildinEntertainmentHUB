#include "TizHubMainComponent.h"

using State = PluginCard::State;

// =============================================================================
//  PluginCard
// =============================================================================

PluginCard::PluginCard (const tiz::PluginInfo& plugin, tiz::HubSettings& s)
    : pluginInfo (plugin), settings (s)
{
    actionButton.onClick = [this] { if (onInstallClicked) onInstallClicked (this); };
    addAndMakeVisible (actionButton);

    // If already installed locally, reflect that
    if (settings.isInstalled (pluginInfo.id))
        setState (State::installed, settings.getInstalledVersion (pluginInfo.id));

    updateActionButton();
}

void PluginCard::paint (juce::Graphics& g)
{
    auto r = getLocalBounds().toFloat();

    // Card background
    g.setColour (juce::Colour (0xff131222u));
    g.fillRoundedRectangle (r, 12.0f);
    g.setColour (juce::Colour (0xff1e2240u));
    g.drawRoundedRectangle (r.reduced (0.5f), 12.0f, 1.0f);

    auto inner = getLocalBounds().reduced (16, 12);

    // ── Row 1: Name + FREE badge ──
    auto row1 = inner.removeFromTop (26);
    auto statusEmoji = pluginInfo.status == "production" ? juce::String ("[OK] ")
                     : pluginInfo.status == "beta"       ? juce::String ("[BETA] ")
                                                         : juce::String ("[DEV] ");
    g.setColour (juce::Colour (0xffe8eaf0u));
    g.setFont (juce::FontOptions (17.0f, juce::Font::bold));
    g.drawText (statusEmoji + pluginInfo.name, row1.removeFromLeft (row1.getWidth() - 110),
                juce::Justification::centredLeft, true);

    // FREE badge
    auto badgeRect = row1.toFloat();
    g.setColour (juce::Colour (0xff164e32u));
    g.fillRoundedRectangle (badgeRect, 6.0f);
    g.setColour (juce::Colour (0xff4ade80u));
    g.setFont (juce::FontOptions (11.0f, juce::Font::bold));
    g.drawText ("FREE VERSION", badgeRect.toNearestInt(), juce::Justification::centred);

    inner.removeFromTop (4);

    // ── Row 2: Description ──
    auto row2 = inner.removeFromTop (20);
    g.setColour (juce::Colour (0xffa0a6bcu));
    g.setFont (juce::FontOptions (13.0f));
    g.drawText (pluginInfo.description, row2, juce::Justification::centredLeft, true);

    inner.removeFromTop (4);

    // ── Row 3: Formats ──
    auto row3 = inner.removeFromTop (20);
    int x = row3.getX();
    g.setFont (juce::FontOptions (11.0f));
    for (auto& fmt : pluginInfo.formats)
    {
        auto w = (int) g.getCurrentFont().getStringWidthFloat (fmt) + 14;
        auto pill = juce::Rectangle<float> ((float) x, (float) row3.getY(), (float) w, 18.0f);
        g.setColour (juce::Colour (0xff1a1d30u));
        g.fillRoundedRectangle (pill, 4.0f);
        g.setColour (juce::Colour (0xffa0a6bcu));
        g.drawText (fmt, pill.toNearestInt(), juce::Justification::centred);
        x += w + 6;
    }

    inner.removeFromTop (4);

    // ── Row 4: Version / status line ──
    auto row4 = inner.removeFromTop (20);
    juce::Colour tagCol;
    juce::String tagText;

    switch (state)
    {
        case State::unchecked:       tagCol = juce::Colour (0xff2a2d48u); tagText = "Waiting...";           break;
        case State::checking:        tagCol = juce::Colour (0xff2a2d48u); tagText = "Checking...";          break;
        case State::hasRelease:      tagCol = juce::Colour (0xff14352au); tagText = versionLabel;            break;
        case State::sourceOnly:      tagCol = juce::Colour (0xff1f1520u); tagText = "FREE SOURCE READY";    break;
        case State::installed:       tagCol = juce::Colour (0xff14352au); tagText = "Installed " + versionLabel; break;
        case State::updateAvailable: tagCol = juce::Colour (0xff422006u); tagText = "Update: " + versionLabel;   break;
        case State::downloading:     tagCol = juce::Colour (0xff2a2d48u); tagText = "Downloading...";       break;
        case State::failed:          tagCol = juce::Colour (0xff3b1010u); tagText = "Check failed";         break;
    }

    auto tagW = juce::jmax (120, (int) g.getCurrentFont().getStringWidthFloat (tagText) + 20);
    auto tagRect = row4.removeFromLeft (tagW).toFloat();
    g.setColour (tagCol);
    g.fillRoundedRectangle (tagRect, 6.0f);

    juce::Colour tagTextCol = (state == State::hasRelease || state == State::installed) ? juce::Colour (0xff22c55eu)
                             : state == State::updateAvailable ? juce::Colour (0xffeab308u)
                             : state == State::sourceOnly ? juce::Colour (0xffa78bfau)
                             : state == State::failed ? juce::Colour (0xffef4444u)
                             : juce::Colour (0xffa0a6bcu);
    g.setColour (tagTextCol);
    g.drawText (tagText, tagRect.toNearestInt(), juce::Justification::centred);
}

void PluginCard::resized()
{
    auto area = getLocalBounds().reduced (16, 12);
    // Action button sits at the right side, vertically centred
    actionButton.setBounds (area.removeFromRight (140).withSizeKeepingCentre (140, 30));
}

void PluginCard::setState (State s, const juce::String& vText)
{
    state = s;
    versionLabel = vText;
    updateActionButton();
    repaint();
}

void PluginCard::updateActionButton()
{
    switch (state)
    {
        case State::unchecked:
        case State::checking:
            actionButton.setButtonText ("...");
            actionButton.setEnabled (false);
            break;
        case State::hasRelease:
        case State::sourceOnly:
            actionButton.setButtonText ("Install");
            actionButton.setEnabled (true);
            break;
        case State::installed:
            actionButton.setButtonText ("Installed");
            actionButton.setEnabled (false);
            break;
        case State::updateAvailable:
            actionButton.setButtonText ("Update");
            actionButton.setEnabled (true);
            break;
        case State::downloading:
            actionButton.setButtonText ("Downloading...");
            actionButton.setEnabled (false);
            break;
        case State::failed:
            actionButton.setButtonText ("Retry");
            actionButton.setEnabled (true);
            break;
    }
}

// =============================================================================
//  TizHubMainComponent
// =============================================================================

TizHubMainComponent::TizHubMainComponent()
{
    // ── Title ──
    titleLabel.setText ("TizWildin Entertainment HUB", juce::dontSendNotification);
    titleLabel.setFont (juce::FontOptions (28.0f, juce::Font::bold));
    titleLabel.setColour (juce::Label::textColourId, juce::Colour (colText));

    subtitleLabel.setText ("Free-version installs, updates, version control & downloads. "
                           "Payments and upgrades live inside each plugin.",
                           juce::dontSendNotification);
    subtitleLabel.setColour (juce::Label::textColourId, juce::Colour (colSub));
    subtitleLabel.setFont (juce::FontOptions (14.0f));

    statsLabel.setColour (juce::Label::textColourId, juce::Colour (colSub));
    statsLabel.setFont (juce::FontOptions (13.0f));

    // ── Buttons ──
    auto styliseButton = [] (juce::TextButton& btn, juce::uint32 bgCol, juce::uint32 textCol)
    {
        btn.setColour (juce::TextButton::buttonColourId,   juce::Colour (bgCol));
        btn.setColour (juce::TextButton::textColourOffId,  juce::Colour (textCol));
    };

    styliseButton (checkAllButton,  colAccent, colText);
    styliseButton (installAllButton, 0xff1b3a26, colGreen);

    checkAllButton.onClick   = [this] { checkAllUpdates(); };
    installAllButton.onClick = [this] { installAll(); };

    autoUpdateToggle.setToggleState (settings.getAutoUpdate(), juce::dontSendNotification);
    autoUpdateToggle.setColour (juce::ToggleButton::textColourId, juce::Colour (colSub));
    autoUpdateToggle.onClick = [this] { settings.setAutoUpdate (autoUpdateToggle.getToggleState()); };

    for (auto* c : { (juce::Component*) &titleLabel, (juce::Component*) &subtitleLabel,
                     (juce::Component*) &statsLabel,  (juce::Component*) &checkAllButton,
                     (juce::Component*) &installAllButton, (juce::Component*) &autoUpdateToggle })
        addAndMakeVisible (c);

    viewport.setViewedComponent (&scrollContent, false);
    viewport.setScrollBarsShown (true, false);
    addAndMakeVisible (viewport);

    buildUI();

    // Auto-check on launch if enabled
    if (settings.getAutoUpdate())
        startTimer (300);  // slight delay so the window paints first
}

TizHubMainComponent::~TizHubMainComponent()
{
    pool.removeAllJobs (true, 4000);
}

void TizHubMainComponent::timerCallback()
{
    stopTimer();
    checkAllUpdates();
}

// ── Build cards grouped by category ──────────────────────────────────────────
void TizHubMainComponent::buildUI()
{
    cards.clear (true);
    sectionLabels.clear (true);
    scrollContent.removeAllChildren();

    for (auto& cat : tiz::getCategories())
    {
        auto pluginsInCat = tiz::getPluginsForCategory (cat.id);
        if (pluginsInCat.isEmpty())
            continue;

        auto* label = sectionLabels.add (new juce::Label());
        label->setText (cat.icon + "  " + cat.name, juce::dontSendNotification);
        label->setFont (juce::FontOptions (16.0f, juce::Font::bold));
        label->setColour (juce::Label::textColourId, juce::Colour (colSub));
        scrollContent.addAndMakeVisible (label);

        for (auto& pluginInfo : pluginsInCat)
        {
            auto* card = cards.add (new PluginCard (pluginInfo, settings));
            card->onInstallClicked = [this] (PluginCard* c) { installPlugin (c); };
            scrollContent.addAndMakeVisible (card);
        }
    }

    updateStats();
}

// ── Layout ───────────────────────────────────────────────────────────────────
void TizHubMainComponent::paint (juce::Graphics& g)
{
    g.fillAll (juce::Colour (colBg));
}

void TizHubMainComponent::resized()
{
    auto area = getLocalBounds().reduced (24);

    // ── Header rows ──
    titleLabel.setBounds (area.removeFromTop (34));
    subtitleLabel.setBounds (area.removeFromTop (22));
    area.removeFromTop (10);

    // ── Controls row ──
    auto controls = area.removeFromTop (36);
    checkAllButton.setBounds (controls.removeFromLeft (160).reduced (0, 2));
    controls.removeFromLeft (8);
    installAllButton.setBounds (controls.removeFromLeft (120).reduced (0, 2));
    controls.removeFromLeft (12);
    autoUpdateToggle.setBounds (controls.removeFromLeft (200).reduced (0, 2));
    statsLabel.setBounds (controls);

    area.removeFromTop (12);

    // ── Scrollable plugin area ──
    viewport.setBounds (area);

    // Lay out scroll contents
    int contentW = viewport.getWidth() - (viewport.isVerticalScrollBarShown() ? 14 : 0);
    int y = 0;
    const int cardH = 136;
    const int sectionGap = 8;
    const int cardGap = 8;

    int cardIdx = 0;
    for (auto& cat : tiz::getCategories())
    {
        auto pluginsInCat = tiz::getPluginsForCategory (cat.id);
        if (pluginsInCat.isEmpty())
            continue;

        // section label
        // Find the matching label by scanning sectionLabels
        for (auto* sl : sectionLabels)
        {
            if (sl->getText().contains (cat.name))
            {
                sl->setBounds (0, y, contentW, 28);
                y += 28 + sectionGap;
                break;
            }
        }

        for (int i = 0; i < pluginsInCat.size() && cardIdx < cards.size(); ++i, ++cardIdx)
        {
            cards[cardIdx]->setBounds (0, y, contentW, cardH);
            y += cardH + cardGap;
        }

        y += 8; // extra gap between sections
    }

    scrollContent.setSize (contentW, juce::jmax (y, viewport.getHeight()));
}

// ── Update checking ──────────────────────────────────────────────────────────
void TizHubMainComponent::checkAllUpdates()
{
    checkAllButton.setEnabled (false);
    checkAllButton.setButtonText ("Checking...");

    for (auto* card : cards)
    {
        card->setState (State::checking);
        checkPlugin (card);
    }
}

void TizHubMainComponent::checkPlugin (PluginCard* card)
{
    auto& plugin = card->getPlugin();

    pool.addJob ([this, card, repo = plugin.repo, pluginId = plugin.id]()
    {
        auto info = github.fetchLatestRelease (repo);

        juce::MessageManager::callAsync ([this, card, info, pluginId]()
        {
            card->releaseInfo = info;

            if (info.found)
            {
                auto installedVer = settings.getInstalledVersion (pluginId);
                if (installedVer.isNotEmpty() && installedVer == info.tagName)
                    card->setState (State::installed, info.tagName);
                else if (installedVer.isNotEmpty())
                    card->setState (State::updateAvailable, info.tagName);
                else
                    card->setState (State::hasRelease, info.tagName);
            }
            else
            {
                card->setState (State::sourceOnly);
            }

            // Check if all done
            bool allDone = true;
            for (auto* c : cards)
                if (c->getState() == State::checking)
                    allDone = false;

            if (allDone)
            {
                checkAllButton.setEnabled (true);
                checkAllButton.setButtonText ("Check All Updates");
                updateStats();
            }
        });
    });
}

// ── Install ──────────────────────────────────────────────────────────────────
void TizHubMainComponent::installPlugin (PluginCard* card)
{
    auto& plugin = card->getPlugin();
    auto& info   = card->releaseInfo;
    card->setState (State::downloading);

    // Pick download URL: prefer platform asset, fall back to source zip, or repo zip
    juce::String downloadUrl = info.assetUrl;
    juce::String filename    = info.assetName;

    if (downloadUrl.isEmpty() && info.sourceZipUrl.isNotEmpty())
    {
        downloadUrl = info.sourceZipUrl;
        filename    = plugin.id + "-source.zip";
    }

    if (downloadUrl.isEmpty())
    {
        // No release at all — open repo in browser as fallback
        juce::URL ("https://github.com/GareBear99/" + plugin.repo).launchInDefaultBrowser();
        card->setState (State::sourceOnly);
        return;
    }

    auto destDir = settings.getInstallRoot();
    destDir.createDirectory();
    auto destFile = destDir.getChildFile (filename);

    pool.addJob ([this, card, downloadUrl, destFile, pluginId = plugin.id,
                  tag = info.tagName]()
    {
        bool ok = github.downloadFile (downloadUrl, destFile);

        juce::MessageManager::callAsync ([this, card, ok, pluginId, tag]()
        {
            if (ok)
            {
                settings.setInstalledVersion (pluginId, tag);
                card->setState (State::installed, tag);
            }
            else
            {
                card->setState (State::failed);
            }
            updateStats();
        });
    });
}

void TizHubMainComponent::installAll()
{
    for (auto* card : cards)
    {
        auto s = card->getState();
        if (s == State::hasRelease || s == State::sourceOnly || s == State::updateAvailable)
            installPlugin (card);
    }
}

// ── Stats ────────────────────────────────────────────────────────────────────
void TizHubMainComponent::updateStats()
{
    int total = cards.size();
    int installed = 0, withRelease = 0, sourceOnly = 0;

    for (auto* card : cards)
    {
        auto s = card->getState();
        if (s == State::installed)                       ++installed;
        if (s == State::hasRelease || s == State::installed || s == State::updateAvailable) ++withRelease;
        if (s == State::sourceOnly)                      ++sourceOnly;
    }

    statsLabel.setText (juce::String (total) + " plugins  |  "
                        + juce::String (installed) + " installed  |  "
                        + juce::String (withRelease) + " with releases  |  "
                        + juce::String (sourceOnly) + " source-only",
                        juce::dontSendNotification);
}
