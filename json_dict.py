import json
import os

def save_dict_to_json(data: dict, file_path: str) -> bool:
    """
    将字典保存为 JSON 文件
    
    参数:
        data: 要保存的字典
        file_path: 保存文件路径（如 "data.json"）
    
    返回:
        保存成功返回 True，失败返回 False
    """
    try:
        # 获取文件所在目录，确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        # 写入 JSON 文件（indent=4 格式化输出，ensure_ascii=False 保留中文）
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"字典已成功保存到 {file_path}")
        return True
    except Exception as e:
        print(f"保存 JSON 失败：{str(e)}")
        return False


def load_json_to_dict(file_path: str) -> dict:
    """
    读取 JSON 文件并转换为字典
    
    参数:
        file_path: JSON 文件路径
    
    返回:
        解析后的字典；若失败返回空字典
    """
    try:
        if not os.path.exists(file_path):
            print(f"文件不存在：{file_path}")
            return {}
        
        # 读取 JSON 文件并解析为字典
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 确保返回的是字典（JSON 可能解析为列表等其他类型）
        if isinstance(data, dict):
            print(f"已从 {file_path} 读取字典")
            return data
        else:
            print(f"JSON 内容不是字典类型（实际类型：{type(data)}）")
            return {}
    except json.JSONDecodeError:
        print(f"JSON 格式错误，无法解析 {file_path}")
        return {}
    except Exception as e:
        print(f"读取 JSON 失败：{str(e)}")
        return {}


# 使用示例
# if __name__ == "__main__":
#     # 1. 定义一个测试字典（包含多种数据类型）
#     test_dict = {
#         "name": "机械革命",
#         "series": ["旷世", "蛟龙", "code"],
#         "specs": {
#             "cpu": "i7-13700H",
#             "gpu": "RTX 4060",
#             "price": 7999
#         },
#         "is_gaming_laptop": True
#     }
    
#     # 2. 保存字典到 JSON 文件
#     json_file = "laptop_info.json"
#     save_dict_to_json(test_dict, json_file)
    
#     # 3. 从 JSON 文件读取字典
#     loaded_dict = load_json_to_dict(json_file)
    
#     # 4. 验证结果
#     if loaded_dict:
#         print("\n读取到的字典内容：")
#         print(f"品牌：{loaded_dict['name']}")
#         print(f"系列：{loaded_dict['series']}")
#         print(f"CPU：{loaded_dict['specs']['cpu']}")