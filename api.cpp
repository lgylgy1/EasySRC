#include <iostream>
#include <string>
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include "config_manager.h"
#include "api.h"

using json = nlohmann::json;
using namespace std;
// 回调函数，用于处理API返回的响应数据
size_t WriteCallback(void* contents, size_t size, size_t nmemb, string* s) {
    size_t newLength = size * nmemb;
    try {
        s->append((char*)contents, newLength);
    }
    catch (bad_alloc& e) {
        // 处理内存分配失败
        return 0;
    }
    return newLength;
}

/**
 * 调用大模型API获取问题答案
 * @param api_url API端点URL
 * @param api_key 访问API的密钥
 * @param question 要问的问题
 * @param answer 用于存储返回答案的字符串引用
 * @return 成功返回true，失败返回false
 */
bool callLLMApi(const u8string& question, string& answer,
    const string& api_url, 
    const string& api_key, 
    const int& max_tokens,
    const string& model) {
    // 初始化curl
    CURL* curl = curl_easy_init();
    if (!curl) {
        cerr << "初始化curl失败" << endl;
        return false;
    }

    // 构建请求体
    json request_data;
    request_data["model"] = model;
    // 显式创建 messages 数组和内部对象
    json messages = json::array();
    json user_message;
    user_message["role"] = "user";
    user_message["content"] = u8string_to_string(question);
    messages.push_back(user_message);  // 将对象添加到数组
    request_data["messages"] = messages;  // 赋值给 messages 字段
    request_data["temperature"] = 0.7;
    request_data["max_tokens"] = max_tokens;  // 设置最大token限制

    string request_body = request_data.dump();

    // 设置curl选项
    struct curl_slist* headers = nullptr;
    headers = curl_slist_append(headers, "Content-Type: application/json");

    // 添加API密钥头部，根据实际API的认证方式修改
    string auth_header = "Authorization: Bearer " + api_key;
    headers = curl_slist_append(headers, auth_header.c_str());

    curl_easy_setopt(curl, CURLOPT_URL, api_url.c_str());
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_POST, 1L);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, request_body.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, request_body.size());

    // 设置响应处理
    string response_string;
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_string);

    // 执行请求
    CURLcode res = curl_easy_perform(curl);
    long http_code = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);

    // 清理curl资源
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);

    // 检查请求是否成功
    if (res != CURLE_OK || http_code != 200) {
        cerr << "API请求失败. 错误代码: " << res
            << ", HTTP状态码: " << http_code << endl;
        cerr << "响应内容: " << response_string << endl;
        return false;
    }

    // 解析JSON响应
    try {
        json response_json = json::parse(response_string);
        // 新增：打印完整响应，分析结构
        //cout << "API 原始响应: " << response_json.dump(4) << endl;
        // 根据实际API的响应格式提取答案
        answer = response_json["choices"][0]["message"]["content"];
        return true;
    }
    catch (json::parse_error& e) {
        cerr << "解析API响应失败: " << e.what() << endl;
        cerr << "响应内容: " << response_string << endl;
        return false;
    }
    catch (exception& e) {
        cerr << "处理API响应时发生错误: " << e.what() << endl;
        return false;
    }
}
