#pragma once
#include <string>

struct TizRuntimeRequest
{
    std::string accountId;
    std::string machineId;
    std::string productId;
    std::string edition;
    std::string runtimeVersion;
};

struct TizRuntimeDecision
{
    bool approved = false;
    std::string reason;
};

class TizPluginBridge
{
public:
    explicit TizPluginBridge(std::string arcBaseUrl);
    TizRuntimeDecision validate(const TizRuntimeRequest& request);
    void openHub();

private:
    std::string arcBaseUrl;
};
