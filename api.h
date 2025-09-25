//api.h
#pragma once
#ifndef API_H
#define API_H
#include <iostream>
#include <string>
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include "config_manager.h"
#include "api.h"
using json = nlohmann::json;

// 将char8_t指针转换为char指针，并构造std::string
constexpr std::string u8string_to_string(const std::u8string_view u8str) {
    return std::string(reinterpret_cast<const char*>(u8str.data()), u8str.size());
}
// 将char指针转换为char8_t指针，并构造std::u8string
constexpr std::u8string string_to_u8string(const std::string str) {
    return std::u8string(reinterpret_cast<const char8_t*>(str.data()), str.size());
}

size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* s);
bool callLLMApi(const std::u8string& question, std::string& answer,
    const std::string& api_url,
    const std::string& api_key,
    const int& max_tokens,
    const std::string& model);
constexpr void split_by_newline(const std::string& str, std::vector<std::string>& lines) {
    size_t start = 0;
    size_t n = str.size();
    for (size_t i = 0; i < n; ++i) {
        if (str[i] == '\n' && i - start > 0) {
            // 提取从 start 到 i-1 的子串（排除 \n）
            lines.push_back(str.substr(start, i - start));
            start = i + 1;
        }
    }
    // 添加最后一行（如果存在）
    if (start < n) {
        lines.push_back(str.substr(start));
    }
    return;
}
#endif

