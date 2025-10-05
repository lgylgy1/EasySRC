import http.client
import json
from urllib.parse import urlparse
from typing import Dict, Optional, Any
from config import Config  # 假设前面的Config类定义在config.py中
import asyncio

async def call_llm_api(config: Config, prompt: str, system_prompt: Optional[str] = None, 
                temperature: float = 0.7, extra_params: Optional[Dict] = None) -> Dict:
    """
    调用大模型API的通用函数（基于Config配置）
    
    参数:
        config: Config类实例，包含API配置信息
        prompt: 用户输入的提示词（必填）
        system_prompt: 系统提示词（可选，用于设定模型行为）
        temperature: 生成温度（0-1，控制随机性）
        extra_params: 额外的API参数（如top_p、frequency_penalty等）
    
    返回:
        解析后的API响应字典（包含生成结果或错误信息）
    """
    # 1. 基础参数校验
    if not config.api_key:
        return {"error": "API密钥不能为空（config.api_key未设置）"}
    if not config.api_url:
        return {"error": "API地址不能为空（config.api_url未设置）"}
    if not prompt.strip():
        return {"error": "提示词（prompt）不能为空"}
    # 2. 解析API URL
    parsed_url = urlparse(config.api_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        return {"error": f"无效的API URL：{config.api_url}（需包含http/https和域名）"}
    # 3. 构建请求参数（兼容主流大模型API格式，如OpenAI风格）
    request_data = {
        "model": config.model,
        "messages": [],
        "max_tokens": config.max_tokens,
        "temperature": temperature
    }
    # 添加系统提示词（如存在）
    if system_prompt and system_prompt.strip():
        request_data["messages"].append({
            "role": "system",
            "content": system_prompt.strip()
        })
    # 添加用户提示词
    request_data["messages"].append({
        "role": "user",
        "content": prompt.strip()
    })
    # 合并额外参数（覆盖默认值）
    if extra_params and isinstance(extra_params, dict):
        request_data.update(extra_params)
    # 4. 构建请求头（包含认证信息）
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.api_key}"  # 主流API的认证格式
    }
    # 5. 发送API请求
    try:
        # 根据协议创建连接（http/https）
        if parsed_url.scheme == "https":
            conn = http.client.HTTPSConnection(parsed_url.netloc, timeout=60)
        else:
            conn = http.client.HTTPConnection(parsed_url.netloc, timeout=60)
        # 拼接请求路径（包含URL中的路径和查询参数）
        request_path = parsed_url.path or "/"
        if parsed_url.query:
            request_path += f"?{parsed_url.query}"
        # 发送POST请求
        conn.request(
            method="POST",
            url=request_path,
            body=json.dumps(request_data).encode("utf-8"),
            headers=headers
        )
        # 获取响应
        response = conn.getresponse()
        status_code = response.status
        response_body = response.read().decode("utf-8")
        conn.close()
        # 解析JSON响应
        try:
            response_json = json.loads(response_body)
        except json.JSONDecodeError:
            return {
                "error": "API返回非JSON格式数据",
                "status_code": status_code,
                "raw_response": response_body
            }
        # 处理HTTP错误状态码
        if status_code >= 400:
            error_msg = response_json.get("error", {}).get("message", "未知错误")
            return {
                "error": f"API请求失败（状态码：{status_code}）",
                "detail": error_msg,
                "status_code": status_code,
                "response": response_json
            }
        # with open("response.json", "w", encoding="utf-8") as f:
        #     f.write(json.dumps(response_json, indent=4))
        # with open("prompt.json", "w", encoding="utf-8") as f:
        #     f.write(json.dumps(request_data, indent=4))
        with open("api_result.txt", "w", encoding="utf-8") as f:
            f.write("prompt: " + prompt + "\n\n" + "response: " + response_json.get("choices", [{}])[0].get("message", {}).get("content") + "\n")
            # print("prompt: " + prompt + "\n\n" + "response: " + response_json.get("choices", [{}])[0].get("message", {}).get("content") + "\n")
        # 正常响应返回
        return {
            "success": True,
            "status_code": status_code,
            "response": response_json,
            # 提取生成的内容（兼容OpenAI风格的响应结构）
            "generated_content": response_json.get("choices", [{}])[0].get("message", {}).get("content")
        }
    except http.client.HTTPException as e:
        return {"error": f"HTTP连接错误：{str(e)}"}
    except TimeoutError:
        return {"error": "API请求超时（超过60秒）"}
    except Exception as e:
        return {"error": f"请求过程出错：{str(e)}"}


# 使用示例
# if __name__ == "__main__":
#     try:
#         # 加载配置
#         config = Config()
#         print("配置加载成功，准备调用API...")
        
#         # 调用大模型API
#         result = asyncio.run(call_llm_api(
#             config=config,
#             system_prompt="你是一个助手，请用简洁的语言回答问题",
#             prompt="介绍一下Python的装饰器",
#             temperature=0.5,
#             extra_params={"top_p": 0.9}  # 额外参数
#         ))
        
#         # 处理返回结果
#         if result.get("success"):
#             print("\nAPI调用成功：")
#             print("生成内容：", result["generated_content"])
#         else:
#             print("\nAPI调用失败：")
#             print("错误信息：", result["error"])
#             if "detail" in result:
#                 print("详细信息：", result["detail"])
    
#     except Exception as e:
#         print(f"初始化失败：{e}")