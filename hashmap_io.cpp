#include "hashmap_io.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>
#include "read_text.h"

// 辅助函数：处理字符串中的特殊字符转义
std::string escapeString(const std::string& s) {
    std::string result;
    for (char c : s) {
        switch (c) {
        case '"': result += "\\\""; break;
        case '\\': result += "\\\\"; break;
        case '\b': result += "\\b"; break;
        case '\f': result += "\\f"; break;
        case '\n': result += "\\n"; break;
        case '\r': result += "\\r"; break;
        case '\t': result += "\\t"; break;
        default: result += c;
        }
    }
    return result;
}

// 辅助函数：反转义字符串
std::string unescapeString(const std::string& s) {
    std::string result;
    for (size_t i = 0; i < s.size(); ++i) {
        if (s[i] == '\\' && i + 1 < s.size()) {
            switch (s[i + 1]) {
            case '"': result += '"'; i++; break;
            case '\\': result += '\\'; i++; break;
            case 'b': result += '\b'; i++; break;
            case 'f': result += '\f'; i++; break;
            case 'n': result += '\n'; i++; break;
            case 'r': result += '\r'; i++; break;
            case 't': result += '\t'; i++; break;
            default: result += s[i];
            }
        }
        else {
            result += s[i];
        }
    }
    return result;
}

// 从字符串b中移除所有出现的子串a
bool removeSubstring(std::string& str, const std::string& substr) {
    std::cout << "str:" << str << "\n" << "substr:" << substr << std::endl;
    // 处理特殊情况：如果a是空字符串则直接返回
    if (substr.empty()) return false;
    size_t pos;
    // 查找并移除第一个出现的a
    if ((pos = str.find(substr)) != std::string::npos) {
        // 从pos位置开始，删除长度为a.size()的字符
        str.erase(pos, substr.size());
        return true;
    }
    return false;
}

//// 保存哈希表到JSON文件
//bool saveHashMapToFile(const std::unordered_map<std::string, std::string>& hashMap, const std::string& filename) {
//    std::ofstream file(filename);
//    if (!file.is_open()) {
//        std::cerr << "无法打开文件进行写入: " << filename << std::endl;
//        return false;
//    }
//
//    file << "{\n";
//    size_t count = 0;
//    const size_t total = hashMap.size();
//
//    for (const auto& pair : hashMap) {
//        file << "    \"" << escapeString(pair.first) << "\": \"" << escapeString(pair.second) << "\"";
//        if (++count < total) {
//            file << ",";
//        }
//        file << "\n";
//    }
//
//    file << "}";
//    return true;
//}
//
//// 从JSON文件加载哈希表
//bool loadHashMapFromFile(std::unordered_map<std::string, std::string>& hashMap, const std::string& filename) {
//    std::ifstream file(filename);
//    if (!file.is_open()) {
//        std::cerr << "无法打开文件进行读取: " << filename << std::endl;
//        return false;
//    }
//    // 读取整个文件内容
//    std::stringstream buffer;
//    buffer << file.rdbuf();
//    std::string content = buffer.str();
//    // 简单的JSON解析（处理基本键值对情况）
//    hashMap.clear();
//    size_t pos = 0;
//    size_t len = content.size();
//    // 跳过开头的'{'
//    while (pos < len && content[pos] != '{') pos++;
//    if (pos >= len) return false;
//    pos++;
//    while (pos < len) {
//        // 跳过空白字符
//        while (pos < len && (content[pos] == ' ' || content[pos] == '\t' || content[pos] == '\n' || content[pos] == '\r')) pos++;
//        if (pos >= len) break;
//        // 检查是否是结束符
//        if (content[pos] == '}') break;
//        // 解析键
//        if (content[pos] != '"') return false;
//        pos++;
//        size_t keyStart = pos;
//        while (pos < len && !(content[pos] == '"' && content[pos - 1] != '\\')) pos++;
//        if (pos >= len || content[pos] != '"') return false;
//        std::string key = content.substr(keyStart, pos - keyStart);
//        key = unescapeString(key);
//        pos++;
//        // 跳过冒号和空白
//        while (pos < len && (content[pos] == ' ' || content[pos] == '\t' || content[pos] == '\n' || content[pos] == '\r')) pos++;
//        if (pos >= len || content[pos] != ':') return false;
//        pos++;
//        while (pos < len && (content[pos] == ' ' || content[pos] == '\t' || content[pos] == '\n' || content[pos] == '\r')) pos++;
//        // 解析值
//        if (pos >= len || content[pos] != '"') return false;
//        pos++;
//        size_t valueStart = pos;
//        while (pos < len && !(content[pos] == '"' && content[pos - 1] != '\\')) pos++;
//        if (pos >= len || content[pos] != '"') return false;
//        std::string value = content.substr(valueStart, pos - valueStart);
//        value = unescapeString(value);
//        pos++;
//        // 添加到哈希表
//        hashMap[key] = value;
//        // 跳过逗号和空白
//        while (pos < len && (content[pos] == ' ' || content[pos] == '\t' || content[pos] == '\n' || content[pos] == '\r')) pos++;
//        if (pos < len && content[pos] == ',') pos++;
//    }
//    return true;
//}
bool saveHashMapToFile(const std::unordered_map<std::string, std::string>& hashMap, const std::string& filename) {
    try {
        // 创建JSON对象并从哈希表初始化
        json j(hashMap);
        // 打开文件并写入JSON内容，设置缩进为4个空格以增强可读性
        std::ofstream file(filename);
        if (!file.is_open()) {
            std::cerr << "无法打开文件进行写入: " << filename << std::endl;
            return false;
        }
        // 使用dump(4)生成带缩进的格式化JSON
        file << j.dump(4);
        return true;
    }
    catch (const std::exception& e) {
        std::cerr << "保存哈希表到文件时发生错误: " << e.what() << std::endl;
        return false;
    }
}

bool loadHashMapFromFile(std::unordered_map<std::string, std::string>& hashMap, const std::string& filename) {
    try {
        // 打开文件并读取内容
        std::ifstream file(filename);
        if (!file.is_open()) {
            std::cerr << "无法打开文件进行读取: " << filename << std::endl;
            return false;
        }
        // 解析JSON内容
        json j;
        file >> j;
        // 将JSON对象转换为哈希表
        hashMap = j.get<std::unordered_map<std::string, std::string>>();
        return true;
    }
    catch (const nlohmann::json::parse_error& e) {
        std::cerr << "JSON解析错误: " << e.what() << " 在位置 " << e.byte << std::endl;
        return false;
    }
    catch (const std::exception& e) {
        std::cerr << "从文件加载哈希表时发生错误: " << e.what() << std::endl;
        return false;
    }
}

void makeHashMap(std::unordered_map<std::string, std::string>& hashMap,
    std::vector<std::string>& lines, std::vector<std::string>& answer_lines) {
    for (auto& line : lines) {
        if (line == "") { std::cout << "line is empty" << std::endl;continue; }
        //line = trim(line);
        for (auto& answer_line : answer_lines) {
            if (answer_line == "") { std::cout << "answer_line is empty" << std::endl;continue; }
            if (removeSubstring(answer_line, line)) {
                //std::cout << "line:" << line << "\nanswer_line:" << answer_line << std::endl;
                hashMap[line] = trim(answer_line);
                answer_line = "";
                break;
            }
        }
    }
}
