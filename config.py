import json
import os
from typing import Dict, List, Optional


class Config:
    def __init__(self, config_path: str = "config.json"):
        """
        初始化配置类，读取并解析配置文件
        
        参数:
            config_path: 配置文件路径，默认为当前目录下的 config.json
        """
        self.config_path = config_path
        self._config: Dict = {}
        self._load_config()
        self._validate_config()

    def _load_config(self) -> None:
        """加载并解析配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        if not os.path.isfile(self.config_path):
            raise IsADirectoryError(f"{self.config_path} 是目录，不是文件")
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误（JSON解析失败）: {str(e)}")
        except PermissionError:
            raise PermissionError(f"没有权限读取配置文件: {self.config_path}")
        except Exception as e:
            raise RuntimeError(f"加载配置文件失败: {str(e)}")
        
    def _validate_config(self) -> None:
        """验证配置项的完整性和类型"""
        required_fields = [
            ("api_key", str),
            ("api_url", str),
            ("model", str),
            ("max_tokens", (str, int)),  # 允许字符串或整数类型
            ("text_extensions", list)
        ]
        # 检查必填字段是否存在
        for field, _ in required_fields:
            if field not in self._config:
                raise KeyError(f"配置文件缺少必填项: {field}")
        # 检查字段类型
        for field, expected_type in required_fields:
            value = self._config[field]
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"配置项 {field} 类型错误，期望 {expected_type}，实际 {type(value)}"
                )
        # 特殊验证：text_extensions 列表元素应为字符串
        for ext in self._config["text_extensions"]:
            if not isinstance(ext, str):
                raise TypeError(f"text_extensions 包含非字符串元素: {ext}")
            
    @property
    def api_key(self) -> str:
        """获取 API 密钥"""
        return self._config["api_key"]

    @property
    def api_url(self) -> str:
        """获取 API 地址"""
        return self._config["api_url"]

    @property
    def model(self) -> str:
        """获取模型名称"""
        return self._config["model"]

    @property
    def max_tokens(self) -> int:
        """获取最大 token 数量（自动转换为整数）"""
        value = self._config["max_tokens"]
        return int(value) if isinstance(value, str) else value

    @property
    def text_extensions(self) -> List[str]:
        """获取需要处理的文件后缀列表"""
        return self._config["text_extensions"].copy()  # 返回副本防止外部修改

    def get(self, key: str, default: Optional[any] = None) -> any:
        """
        获取配置项（支持获取非预定义的额外配置）
        
        参数:
            key: 配置项键名
            default: 默认值
        
        返回:
            配置项值或默认值
        """
        return self._config.get(key, default)

    def __str__(self) -> str:
        """字符串表示（隐藏敏感信息）"""
        masked_config = self._config.copy()
        if "api_key" in masked_config:
            # 隐藏 API 密钥中间部分
            api_key = masked_config["api_key"]
            if len(api_key) > 6:
                masked_config["api_key"] = api_key[:3] + "***" + api_key[-3:]
        return json.dumps(masked_config, indent=2, ensure_ascii=False)

config = Config()
# 使用示例
# if __name__ == "__main__":
#     try:
#         config = Config()
#         print("配置加载成功:")
#         print(config)
        
#         # 访问配置项示例
#         print("\nAPI 地址:", config.api_url)
#         print("模型名称:", config.model)
#         print("最大 Token 数:", config.max_tokens, type(config.max_tokens))
#         print("文件后缀列表:", config.text_extensions)
#     except Exception as e:
#         print(f"配置加载失败: {e}")