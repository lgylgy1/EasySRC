#include <iostream>
#include <string>
#include "config_manager.h"
#include "api.h"
#include <Windows.h>
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include "read_text.h"
#include <fstream>
#include "hashmap_io.h"

using namespace std;
// 设置控制台输入输出为UTF-8编码
void set_console_to_utf8() {
    // 获取标准输出和输入句柄
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    HANDLE hIn = GetStdHandle(STD_INPUT_HANDLE);

    // 设置控制台输出编码为UTF-8
    SetConsoleOutputCP(CP_UTF8);
    // 设置控制台输入编码为UTF-8
    SetConsoleCP(CP_UTF8);
}

// 将文件路径修改为：原文件所在目录/指定文件夹/原文件名
// 参数：
//   original_path - 原始文件路径
//   target_folder - 目标文件夹名称（相对于原文件所在目录）
// 返回：修改后的路径
// 若指定文件夹不存在，则自动创建
fs::path move_path_to_folder(const fs::path& original_path, const std::string& target_folder) {
    // 检查原始文件是否存在
    if (!fs::exists(original_path)) {
        throw std::invalid_argument("原始文件不存在: " + original_path.string());
    }
    if (!fs::is_regular_file(original_path)) {
        throw std::invalid_argument("路径不是文件: " + original_path.string());
    }

    // 1. 解析原始路径的目录和文件名
    fs::path parent_dir = original_path.parent_path();
    if (parent_dir.empty()) {
        parent_dir = fs::current_path(); // 处理当前目录下的文件
    }
    fs::path filename = original_path.filename(); // 保留原文件名

    // 2. 构建目标文件夹和目标路径
    fs::path target_dir = parent_dir / target_folder;
    fs::path target_path = target_dir / filename;

    // 3. 若目标文件夹不存在，则创建（包括所有必要的父目录）
    if (!fs::exists(target_dir)) {
        try {
            // create_directories：递归创建目录，支持多级目录（如 a/b/c）
            if (!fs::create_directories(target_dir)) {
                throw std::runtime_error("创建文件夹失败（未知原因）");
            }
            std::cout << "已创建文件夹: " << target_dir << std::endl;
        }
        catch (const fs::filesystem_error& e) {
            throw std::runtime_error("创建文件夹失败: " + std::string(e.what()));
        }
    }

    return target_path;
}
// 示例用法 
int main(int argc, char* argv[]) {
    std::wstring dir_wstr;
    // 优先命令行参数中获取路径（如果提供了参数）
    if (argc > 1) {
        dir_wstr = charToWstring(argv[1]);  // 使用第一个个参数作为路径
    }
    else {
        // 否则从控制台读取宽字符输入
        std::wcout.imbue(std::locale(""));
        wcout << L"请输入要搜索的目录路径: ";
        getline(std::wcin, dir_wstr);  // 使用 wcin 匹配 wstring
    }
    // 构造文件系统路径
    fs::path dir_path(dir_wstr);
    // 验证路径
    if (!fs::exists(dir_path)) {
        cout << "无效路径" << endl;
    }

    set_console_to_utf8();

    ConfigManager configManager = ConfigManager();
    std::optional<Config> opt_config = configManager.get_config();
    Config config = opt_config.value_or(Config());
    std::cout << "api_key:" << config.api_key << std::endl;
    std::cout << "api_url:" << config.api_url << std::endl;
    std::cout << "max_token:" << config.max_tokens << std::endl;
    std::cout << "model:" << config.model << std::endl;
    std::unordered_map<std::string, std::string> hashMap;
    if (loadHashMapFromFile(hashMap, "hashmap.json")) {
        std::cout << "\n从文件恢复的哈希表内容：" << std::endl;
        //for (const auto& pair : hashMap) {
        //    std::cout << pair.first << " : " << pair.second << std::endl;
        //}
    }
    else {
        std::cerr << "恢复哈希表失败" << std::endl;
    }

    std::unordered_set<std::string> text_extension(config.text_extensions.begin(), config.text_extensions.end());
    
    std::vector<std::pair<fs::path, std::pair<Encoding, std::string>>> file_contents;
    if(fs::is_directory(dir_path)){find_and_read_text_files(dir_path, text_extension, file_contents);}
    else{
        Encoding encoding;
        std::string content = read_text_file(dir_path, &encoding);
        if (!content.empty()) {
            file_contents.emplace_back(dir_path, std::make_pair(encoding, content));
        }
    }
    // 输出结果统计
    std::cout << "\n找到 " << file_contents.size() << " 个文本文件:\n" << std::endl;
    // 打印每个文件的信息
    for (const auto& [path, data] : file_contents) {
        const auto& [encoding, content] = data;
        std::cout << "----------------------------------------" << std::endl;
        std::cout << "文件: " << path << std::endl;
        std::cout << "编码: " << get_encoding_name(encoding) << std::endl;
        std::cout << "内容长度: " << content.size() << " 字节" << std::endl;
        // 打印前500个字符预览
        std::cout << "内容预览:\n";
        if (content.size() > 500) {
            std::cout << content.substr(0, 500) << "..." << std::endl;
        }
        else {
            std::cout << content << std::endl;
        }
        std::cout << std::endl;
    }
    // 初始化curl全局环境
    curl_global_init(CURL_GLOBAL_DEFAULT);
    for (const auto& [path, data] : file_contents) {
        const auto& [encoding, content] = data;
        vector<string> lines;
        split_by_newline(content, lines);
        ofstream file(move_path_to_folder(path, "README"), std::ios::app);
        u8string code;
        string line;
        for (int i = 0; i < lines.size();++i) {
            line = lines[i];
            if (line == "" || i==lines.size()-1 || code.length() > 10000) {
                u8string question = u8"路径：" + path.u8string() + u8"的文件中包含如下代码："
                    + code + u8"请给出逐行详细注释后的代码，只给出带有注释的代码即可";
                string answer;
                bool success = callLLMApi(question, answer,
                    config.api_url,
                    config.api_key,
                    config.max_tokens,
                    config.model);
                if (success) {                    
                    cout << "问题: " << u8string_to_string(question) << endl << endl;
                    cout << "回答: " << answer << endl;
                    vector<string> answer_lines;
                    split_by_newline(answer, answer_lines);
                    makeHashMap(hashMap, lines, answer_lines);
                    if (saveHashMapToFile(hashMap, "hashmap.json")) {
                        std::cout << "哈希表已成功保存到文件" << std::endl;
                    }
                    else {
                        std::cerr << "保存哈希表失败" << std::endl;
                        return 1;
                    }
                }
                else {
                    cerr << "获取回答失败" << endl;
                }
                if (!file.is_open()) {
                    std::cerr << "无法打开文件" << std::endl;
                    return false;
                }
                // 写入内容
                file << (answer+"\n");
                code = u8"";
            }
            else {
                code += (string_to_u8string(line)+u8"\n");
            }
        }
        file.close();
    }
    // 清理curl全局环境
    curl_global_cleanup();
    return 0;
}
