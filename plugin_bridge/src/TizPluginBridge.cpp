#include "TizPluginBridge.h"

TizPluginBridge::TizPluginBridge(std::string url)
    : arcBaseUrl(std::move(url))
{
}

TizRuntimeDecision TizPluginBridge::validate(const TizRuntimeRequest&)
{
    return { true, "stub_validate_with_arc" };
}

void TizPluginBridge::openHub()
{
    // TODO: launch TizWildin Hub executable
}
