#include "TizPluginBridge.h"
#include <sstream>
#include <utility>
#include <cstdlib>
#include <curl/curl.h>

namespace
{
size_t writeCallback(void* contents, size_t size, size_t nmemb, void* userp)
{
    auto total = size * nmemb;
    auto* output = static_cast<std::string*>(userp);
    output->append(static_cast<char*>(contents), total);
    return total;
}

std::string escapeJson(const std::string& input)
{
    std::string out;
    out.reserve(input.size());
    for (char c : input)
    {
        switch (c)
        {
            case '"': out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default: out += c; break;
        }
    }
    return out;
}
}

TizPluginBridge::TizPluginBridge(std::string url)
    : arcBaseUrl(std::move(url))
{
}

TizRuntimeDecision TizPluginBridge::validate(const TizRuntimeRequest& request)
{
    CURL* curl = curl_easy_init();
    if (!curl)
        return { false, "curl_init_failed" };

    std::string response;
    std::ostringstream body;
    body
        << "{"
        << "\"accountId\":\"" << escapeJson(request.accountId) << "\","
        << "\"machineId\":\"" << escapeJson(request.machineId) << "\","
        << "\"productId\":\"" << escapeJson(request.productId) << "\","
        << "\"edition\":\"" << escapeJson(request.edition) << "\","
        << "\"runtimeVersion\":\"" << escapeJson(request.runtimeVersion) << "\""
        << "}";

    auto url = arcBaseUrl + "/validate-runtime";
    struct curl_slist* headers = nullptr;
    headers = curl_slist_append(headers, "Content-Type: application/json");

    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, body.str().c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT_MS, 2500L);

    auto result = curl_easy_perform(curl);
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);

    if (result != CURLE_OK)
        return { false, "arc_unreachable" };

    if (response.find("\"approved\":true") != std::string::npos)
        return { true, "approved" };

    if (response.find("payment_issue") != std::string::npos)
        return { false, "payment_issue" };
    if (response.find("seat_limit_reached") != std::string::npos)
        return { false, "seat_limit_reached" };
    if (response.find("not_owned") != std::string::npos)
        return { false, "not_owned" };

    return { false, "denied" };
}

void TizPluginBridge::openHub()
{
#if defined(_WIN32)
    std::system("start TizWildinEntertainmentHUB.exe");
#elif defined(__APPLE__)
    std::system("open -a TizWildin\\ Entertainment\\ HUB");
#else
    std::system("TizWildinEntertainmentHUB &");
#endif
}
