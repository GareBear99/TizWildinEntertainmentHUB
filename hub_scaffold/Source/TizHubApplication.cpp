#include "TizHubApplication.h"
#include "TizHubMainComponent.h"

void TizHubApplication::initialise (const juce::String&)
{
    mainWindow = std::make_unique<juce::DocumentWindow>(
        "TizWildin Hub",
        juce::Colours::black,
        juce::DocumentWindow::allButtons);

    mainWindow->setUsingNativeTitleBar(true);
    mainWindow->setResizable(true, true);
    mainWindow->setContentOwned(new TizHubMainComponent(), true);
    mainWindow->centreWithSize(1280, 820);
    mainWindow->setVisible(true);
}

void TizHubApplication::shutdown()
{
    mainWindow.reset();
}
