// config_manager.cpp
#include "config_manager.h"
#include "nlohmann/json.hpp"
#include <fstream>
#include <iostream>
#include <filesystem>

namespace fs = std::filesystem;
using json = nlohmann::json;

// 构造函数
ConfigManager::ConfigManager(std::u8string path)
    : config_path(std::move(path)), loaded(false) {
    ConfigManager::load();
}

std::ifstream open_file_with_filesystem(const std::u8string& u8path) {
    // C++17的filesystem::path支持从char8_t*构造
    std::filesystem::path path(u8path);
    // 转换为系统原生路径格式
    return std::ifstream(path, std::ios::in);
}

// 加载配置文件
bool ConfigManager::load() {
    try {
        if (!config_file_exists()) {
            std::cerr << "配置文件不存在" << std::endl;
            return false;
        }
        std::ifstream file = open_file_with_filesystem(config_path);
        if (!file.is_open()) {
            std::cerr << "无法打开配置文件" << std::endl;
            return false;
        }
        json j;
        file >> j;
        // 读取配置项，不存在则使用默认值
        config_data.api_key = j["api_key"];
        config_data.api_url = j["api_url"];
        config_data.model = j["model"];
        config_data.max_tokens = j["max_tokens"];
        if (j.contains("text_extensions") && j["text_extensions"].is_array()) {
            config_data.text_extensions = j["text_extensions"].get<std::vector<std::string>>();
        }
        else {
            // 可选：配置项不存在时设置默认扩展名列表
            config_data.text_extensions = { ".txt", ".cpp", ".h", ".md", ".json" };
        }
        loaded = true;
        return true;
    }
    catch (const std::exception& e) {
        std::cerr << "加载配置失败: " << e.what() << std::endl;
        return false;
    }
}

// 获取配置数据
std::optional<Config> ConfigManager::get_config() const {
    if (loaded) {
        return config_data;
    }
    return std::nullopt;
}

// 更新配置
void ConfigManager::update_config(const Config& new_config) {
    config_data = new_config;
    loaded = true;
}

// 检查配置文件是否存在
bool ConfigManager::config_file_exists() const {
    return fs::exists(config_path) && fs::is_regular_file(config_path);
}