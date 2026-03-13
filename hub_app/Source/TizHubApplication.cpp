#include "TizHubApplication.h"
#include "TizHubMainComponent.h"

namespace
{
class HubWindow : public juce::DocumentWindow
{
public:
    HubWindow() : juce::DocumentWindow("TizWildin Entertainment HUB", juce::Colours::black, juce::DocumentWindow::allButtons)
    {
        setUsingNativeTitleBar(true);
        setResizable(true, true);
        setResizeLimits(1080, 700, 1800, 1200);
        setContentOwned(new TizHubMainComponent(), true);
        centreWithSize(1360, 860);
        setVisible(true);
    }

    void closeButtonPressed() override
    {
        juce::JUCEApplication::getInstance()->systemRequestedQuit();
    }
};
}

void TizHubApplication::initialise(const juce::String&)
{
    mainWindow = std::make_unique<HubWindow>();
}

void TizHubApplication::shutdown()
{
    mainWindow.reset();
}
