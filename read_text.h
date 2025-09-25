#pragma once
#ifndef READ_TEXT_H
#define READ_TEXT_H
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <vector>
#include <Windows.h>
#include <memory>
#include "config_manager.h"
#include <unordered_set>

namespace fs = std::filesystem;

// 编码类型枚举
enum class Encoding {
    UNKNOWN,
    EMPTY,
    ASCII,
    UTF8_BOM,
    UTF8,
    UTF16_LE,
    UTF16_BE,
    GBK
};

Encoding detect_encoding(const fs::path& file_path);
std::string wstring_to_string(const std::wstring& wstr, UINT code_page);
std::wstring string_to_wstring(const std::string& str, UINT code_page);
std::string read_text_file(const fs::path& file_path, Encoding* out_encoding = nullptr);
void find_and_read_text_files(
    const fs::path& directory,
    const std::unordered_set<std::string>& text_extensions,  // 修正参数名（复数）
    std::vector<std::pair<fs::path, std::pair<Encoding, std::string>>>& results
);
std::string get_encoding_name(Encoding encoding);
std::string trim(const std::string& str);
int splitByNewline(const std::string& str, std::vector<std::string>& result);
std::string trim(const std::string& str);
std::wstring charToWstring(const char* str);
#endif // !READ_TEXT_H

