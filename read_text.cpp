#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <vector>
#include <Windows.h>
#include <memory>
#include "config_manager.h"
#include <unordered_set>
#include "read_text.h"

// 检测文件编码
Encoding detect_encoding(const fs::path& file_path) {
    std::ifstream file(file_path, std::ios::binary);
    if (!file.is_open()) {
        return Encoding::UNKNOWN;
    }
    // 检查文件是否为空
    file.seekg(0, std::ios::end);
    std::streamsize file_size = file.tellg();
    if (file_size == 0) {
        return Encoding::EMPTY;
    }
    file.seekg(0);
    // 读取BOM（最多4字节）
    unsigned char bom[4] = { 0 };
    file.read(reinterpret_cast<char*>(bom), 4);
    std::streamsize bytes_read = file.gcount();
    // 检测BOM
    if (bytes_read >= 3 && bom[0] == 0xEF && bom[1] == 0xBB && bom[2] == 0xBF) {
        return Encoding::UTF8_BOM;
    }
    if (bytes_read >= 2) {
        if (bom[0] == 0xFF && bom[1] == 0xFE) {
            return Encoding::UTF16_LE;
        }
        if (bom[0] == 0xFE && bom[1] == 0xFF) {
            return Encoding::UTF16_BE;
        }
    }
    // 回退到文件开头，准备检测UTF-8
    file.seekg(0);
    bool likely_utf8 = true;
    char c;
    int consecutive_ones = 0;
    const int MAX_CHECK_BYTES = 1024; // 最多检查前1024字节
    int checked_bytes = 0;
    while (checked_bytes < MAX_CHECK_BYTES && file.get(c)) {
        checked_bytes++;
        unsigned char uc = static_cast<unsigned char>(c);
        if ((uc & 0x80) == 0) { // 单字节字符（0xxxxxxx）
            consecutive_ones = 0;
            continue;
        }
        // 多字节序列处理
        if (consecutive_ones == 0) {
            // 检查是否为多字节起始字节（11xxxxxx）
            if ((uc & 0x40) == 0) {
                likely_utf8 = false;
                break;
            }
            // 计算后续需要的字节数（连续1的数量）
            unsigned char mask = 0x20;
            consecutive_ones = 1;
            while ((uc & mask) != 0) {
                consecutive_ones++;
                mask >>= 1;
                if (consecutive_ones > 3) { // UTF-8最多4字节（11110xxx）
                    likely_utf8 = false;
                    break;
                }
            }
            if (!likely_utf8) break;
        }
        else {
            // 检查是否为后续字节（10xxxxxx）
            if ((uc & 0xC0) != 0x80) {
                likely_utf8 = false;
                break;
            }
            consecutive_ones--;
        }
    }
    // 检查是否为纯ASCII
    if (!likely_utf8) {
        file.seekg(0);
        bool is_ascii = true;
        checked_bytes = 0;
        while (checked_bytes < MAX_CHECK_BYTES && file.get(c)) {
            checked_bytes++;
            if (static_cast<unsigned char>(c) > 0x7F) {
                is_ascii = false;
                break;
            }
        }
        if (is_ascii) {
            return Encoding::ASCII;
        }
    }
    return likely_utf8 ? Encoding::UTF8 : Encoding::UNKNOWN;
}

// 编码转换：WideCharToMultiByte的封装
std::string wstring_to_string(const std::wstring& wstr, UINT code_page) {
    if (wstr.empty()) return "";
    // 计算转换所需长度（排除终止符，避免重复计算）
    int length = WideCharToMultiByte(
        code_page,
        0,
        wstr.c_str(),
        static_cast<int>(wstr.size()), // 显式指定长度，避免-1导致的终止符冗余
        nullptr,
        0,
        nullptr, nullptr
    );
    if (length <= 0) return "";
    std::unique_ptr<char[]> buffer(new char[length + 1]); // +1 预留终止符位置
    // 执行转换
    int result = WideCharToMultiByte(
        code_page,
        0,
        wstr.c_str(),
        static_cast<int>(wstr.size()),
        buffer.get(),
        length,
        nullptr, nullptr
    );
    if (result <= 0) return "";
    buffer[length] = '\0'; // 手动添加终止符
    return std::string(buffer.get());
}

// 编码转换：MultiByteToWideChar的封装
std::wstring string_to_wstring(const std::string& str, UINT code_page) {
    if (str.empty()) return L"";
    // 计算转换所需长度
    int length = MultiByteToWideChar(
        code_page,
        0,
        str.c_str(),
        static_cast<int>(str.size()), // 显式指定长度
        nullptr,
        0
    );
    if (length <= 0) return L"";
    std::unique_ptr<wchar_t[]> buffer(new wchar_t[length + 1]); // +1 预留终止符
    // 执行转换
    int result = MultiByteToWideChar(
        code_page,
        0,
        str.c_str(),
        static_cast<int>(str.size()),
        buffer.get(),
        length
    );
    if (result <= 0) return L"";
    buffer[length] = L'\0'; // 手动添加终止符
    return std::wstring(buffer.get());
}

// 读取不同编码的文本文件，统一转换为UTF-8输出（完善 EMPTY/ASCII 处理）
std::string read_text_file(const fs::path& file_path, Encoding* out_encoding) {
    try {
        // 检测编码
        Encoding encoding = detect_encoding(file_path);
        if (out_encoding != nullptr) {
            *out_encoding = encoding; // 确保指针非空再赋值
        }

        // 特殊编码：空文件直接返回空字符串
        if (encoding == Encoding::EMPTY) {
            return "";
        }

        // 打开文件（二进制模式，保留原始字节）
        std::ifstream file(file_path, std::ios::binary);
        if (!file.is_open()) {
            throw std::runtime_error("无法打开文件（路径：" + file_path.string() + "）");
        }

        // 读取文件内容（空文件已提前处理，此处无需额外判断）
        std::string content((std::istreambuf_iterator<char>(file)),
            std::istreambuf_iterator<char>());

        // 根据编码转换为UTF-8
        switch (encoding) {
        case Encoding::UTF8_BOM:
            // 去除BOM头（前3字节），避免UTF-8解析异常
            return (content.size() >= 3) ? content.substr(3) : content;

        case Encoding::UTF8:
        case Encoding::ASCII: // ASCII 是 UTF-8 的子集，可直接返回
            return content;

        case Encoding::GBK:
            // GBK → 宽字符串（UTF-16）→ UTF-8
            return wstring_to_string(string_to_wstring(content, 936), CP_UTF8);

        case Encoding::UTF16_LE: {
            // UTF-16 LE 带BOM：跳过前2字节（FF FE），直接转换
            size_t start_idx = 2;
            if (content.size() < start_idx) {
                throw std::runtime_error("UTF-16 LE 文件内容过短");
            }
            // 按 wchar_t 解析（Windows 下 wchar_t 为 2 字节，匹配 UTF-16 LE）
            const wchar_t* wstr_ptr = reinterpret_cast<const wchar_t*>(content.data() + start_idx);
            size_t wstr_len = (content.size() - start_idx) / sizeof(wchar_t);
            std::wstring wstr(wstr_ptr, wstr_len);
            return wstring_to_string(wstr, CP_UTF8);
        }

        case Encoding::UTF16_BE: {
            // UTF-16 BE 带BOM：跳过前2字节（FE FF），转换字节序为 LE 后再处理
            size_t start_idx = 2;
            if (content.size() < start_idx) {
                throw std::runtime_error("UTF-16 BE 文件内容过短");
            }
            std::wstring wstr;
            // 遍历字节，交换高低位（BE → LE）
            for (size_t i = start_idx; i + 1 < content.size(); i += 2) {
                wchar_t le_char = (static_cast<wchar_t>(content[i + 1]) << 0) |  // 低位字节
                    (static_cast<wchar_t>(content[i]) << 8);     // 高位字节
                wstr.push_back(le_char);
            }
            return wstring_to_string(wstr, CP_UTF8);
        }

        case Encoding::UNKNOWN: { // 关键修复：用 {} 创建独立作用域
            // 未知编码：先尝试ASCII/UTF-8，失败再尝试GBK（避免盲目转GBK导致乱码）
            if (content.empty()) return "";
            // 检查是否为纯ASCII（可直接作为UTF-8）
            bool is_ascii = true; // 变量在独立作用域内，无跳转冲突
            for (unsigned char uc : content) {
                if (uc > 0x7F) {
                    is_ascii = false;
                    break;
                }
            }
            if (is_ascii) {
                if (out_encoding != nullptr) *out_encoding = Encoding::ASCII; // 修正编码标识
                return content;
            }
            // 非ASCII：尝试GBK转换
            std::cerr << "警告：文件 " << file_path << " 编码未知，尝试按GBK处理" << std::endl;
            return wstring_to_string(string_to_wstring(content, 936), CP_UTF8);
        }
        default:
            return "";
        }
    }
    catch (const std::exception& e) {
        std::cerr << "读取文件失败: " << e.what() << std::endl;
        if (out_encoding != nullptr) *out_encoding = Encoding::UNKNOWN; // 异常时标记为未知编码
        return "";
    }
}

// 递归查找所有文本文件并读取内容
void find_and_read_text_files(
    const fs::path& directory,
    const std::unordered_set<std::string>& text_extensions,  // 修正参数名（复数）
    std::vector<std::pair<fs::path, std::pair<Encoding, std::string>>>& results
) {
    try {
        if (!fs::exists(directory) || !fs::is_directory(directory)) {
            std::cerr << "路径 " << directory << " 不存在或不是目录" << std::endl;
            return;
        }
        // 遍历目录
        for (const auto& entry : fs::recursive_directory_iterator(directory)) {
            if (entry.is_regular_file()) {  // 先判断是否为常规文件
                fs::path ext_path = entry.path().extension();  // 获取扩展名（如".TXT"）
                // 过滤无扩展名的文件
                if (ext_path.empty()) {
                    continue;
                }
                // 将扩展名转为小写（关键改进：统一大小写）
                std::string ext = ext_path.string();  // 转为字符串
                for (char& c : ext) {
                    c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
                }
                // 检查是否在文本扩展名集合中
                if (text_extensions.count(ext) != 0) {
                    Encoding encoding;
                    std::string content = read_text_file(entry.path(), &encoding);
                    if (!content.empty()) {
                        results.emplace_back(entry.path(), std::make_pair(encoding, content));
                    }
                }
            }
        }
    }
    catch (const fs::filesystem_error& e) {
        std::cerr << "文件系统错误: " << e.what() << std::endl;
    }
    catch (const std::exception& e) {
        std::cerr << "错误: " << e.what() << std::endl;
    }
}

// 获取编码名称（补充 EMPTY/ASCII 对应的名称）
std::string get_encoding_name(Encoding encoding) {
    switch (encoding) {
    case Encoding::UNKNOWN:    return "未知编码";
    case Encoding::EMPTY:      return "空文件";
    case Encoding::ASCII:      return "ASCII";
    case Encoding::UTF8_BOM:   return "UTF-8 (带BOM)";
    case Encoding::UTF8:       return "UTF-8 (无BOM)";
    case Encoding::GBK:        return "GBK/GB2312";
    case Encoding::UTF16_LE:   return "UTF-16 LE (带BOM)";
    case Encoding::UTF16_BE:   return "UTF-16 BE (带BOM)";
    default:                   return "未定义编码";
    }
}

// 去除字符串首尾的空白字符
std::string trim(const std::string& str) {
    // 处理空字符串情况
    if (str.empty()) {
        return str;
    }
    // 找到第一个非空白字符的位置
    size_t start = 0;
    while (start < str.size() && std::isspace(static_cast<unsigned char>(str[start]))) {
        start++;
    }
    // 找到最后一个非空白字符的位置
    size_t end = str.size() - 1;
    while (end > start && std::isspace(static_cast<unsigned char>(str[end]))) {
        end--;
    }
    // 返回裁剪后的子字符串
    return str.substr(start, end - start + 1);
}

// 拆分字符串
int splitByNewline(const std::string& str, std::vector<std::string>& result) {
    std::string currentLine;

    for (char c : str) {
        // 遇到换行符时，将当前累积的字符串添加到结果中，并重置当前字符串
        if (c == '\n') {
            result.push_back(currentLine);
            currentLine.clear();
        }
        else {
            // 否则继续累积字符
            currentLine += c;
        }
    }
    // 添加最后一行（如果存在）
    if (!currentLine.empty()) {
        result.push_back(currentLine);
    }
    return result.size();
}

// 将 char* (ANSI) 转换为 wstring
std::wstring charToWstring(const char* str) {
    // 计算需要的宽字符缓冲区大小
    int len = MultiByteToWideChar(CP_ACP, 0, str, -1, nullptr, 0);
    if (len == 0) {
        return L"";
    }
    // 分配缓冲区并进行转换
    std::wstring wstr(len, L'\0');
    MultiByteToWideChar(CP_ACP, 0, str, -1, &wstr[0], len);
    // 移除末尾的空字符
    wstr.pop_back();
    return wstr;
}

//int main() {
//    // 设置控制台为UTF-8输出
//    SetConsoleOutputCP(CP_UTF8);
//    ConfigManager configManager = ConfigManager();
//    std::optional<Config> opt_config = configManager.get_config();
//    Config config = opt_config.value_or(Config());
//    std::cout << "api_key:" << config.api_key << std::endl;
//    std::cout << "api_url:" << config.api_url << std::endl;
//    std::cout << "max_token:" << config.max_tokens << std::endl;
//    std::cout << "model:" << config.model << std::endl;
//    std::unordered_set<std::string> text_extension(config.text_extensions.begin(), config.text_extensions.end());
//    // 指定要搜索的目录路径
//    std::string dir_path = "D:\\c++\\VS_project\\test";
//    /*std::cout << "请输入要搜索的目录路径: ";
//    std::getline(std::cin, dir_path);*/
//
//    // 存储结果：文件路径 -> (编码, 内容)
//    std::vector<std::pair<fs::path, std::pair<Encoding, std::string>>> file_contents;
//
//    // 查找并读取所有文本文件
//    find_and_read_text_files(dir_path, text_extension, file_contents);
//
//    // 输出结果统计
//    std::cout << "\n找到 " << file_contents.size() << " 个文本文件:\n" << std::endl;
//
//    // 打印每个文件的信息
//    for (const auto& [path, data] : file_contents) {
//        const auto& [encoding, content] = data;
//        std::cout << "----------------------------------------" << std::endl;
//        std::cout << "文件: " << path << std::endl;
//        std::cout << "编码: " << get_encoding_name(encoding) << std::endl;
//        std::cout << "内容长度: " << content.size() << " 字节" << std::endl;
//
//        // 打印前500个字符预览
//        std::cout << "内容预览:\n";
//        if (content.size() > 500) {
//            std::cout << content.substr(0, 500) << "..." << std::endl;
//        }
//        else {
//            std::cout << content << std::endl;
//        }
//        std::cout << std::endl;
//    }
//
//    return 0;
//}
