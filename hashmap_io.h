#pragma once
#ifndef HASHMAP_IO_H
#define HASHMAP_IO_H
#include <unordered_map>
#include <string>
#include "nlohmann/json.hpp"

// 为方便使用，定义json别名
using json = nlohmann::json;

// 将哈希表保存到JSON文件
bool saveHashMapToFile(const std::unordered_map<std::string, std::string>& hashMap, const std::string& filename);

// 从JSON文件恢复哈希表
bool loadHashMapFromFile(std::unordered_map<std::string, std::string>& hashMap, const std::string& filename);

void makeHashMap(std::unordered_map<std::string, std::string>& hashMap,
    std::vector<std::string>& lines, std::vector<std::string>& answer_lines);
#endif // !HASHMAP_IO_H

