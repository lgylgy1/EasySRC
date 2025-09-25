// config_manager.h
#pragma once
#ifndef CONFIG_MANAGER_H
#define CONFIG_MANAGER_H

#include <string>
#include <optional>
#include <vector>

// 配置数据结构
struct Config {
    std::string api_key;
    std::string api_url;
    std::string model;
    int max_tokens;
    std::vector<std::string> text_extensions;
};
// 配置管理器类
class ConfigManager {
private:
    std::u8string config_path;
    Config config_data;
    bool loaded;
public:
    // 构造函数，接受配置文件路径
    explicit ConfigManager(std::u8string path = u8"config.json");
    // 加载配置文件
    bool load();
    // 获取配置数据
    std::optional<Config> get_config() const;
    // 更新配置
    void update_config(const Config& new_config);
    // 检查配置文件是否存在
    bool config_file_exists() const;
};

#endif // CONFIG_MANAGER_H

