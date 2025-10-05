import re
from typing import List, Optional

def extract_code_blocks(text: str) -> List[str]:
    """
    提取字符串中被 ``` 嵌套的代码块内容
    
    参数:
        text: 包含 ``` 代码块的原始字符串
        
    返回:
        提取到的代码块列表（不含 ``` 标记和语言标识）
    """
    # 正则表达式说明：
    # - ```(.*?) 匹配起始的 ``` 及可能的语言标识（非贪婪匹配）
    # - (.*?) 匹配代码块内容（非贪婪匹配，支持多行）
    # - ``` 匹配结束的 ```
    # - re.DOTALL 使 . 匹配包括换行符在内的所有字符
    pattern = r'```(.*?)\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    code_blocks = []
    for lang, content in matches:
        # 去除内容前后的空行和空白字符
        cleaned_content = content.strip()
        if cleaned_content:  # 只保留非空内容
            code_blocks.append(cleaned_content)
    
    return code_blocks

# s="""
# response: ```cpp
#                     if (!_STD _Could_compare_equal_to_value_type<_It>(_Value)) {  // 检查迭代器指向的值类型是否可以与_Value进行相等比较
#                         return {_First + _Count, _First + _Count};  // 如果不能比较，返回范围末尾的子范围
#                     }
#                         }
#                         break;  // 退出循环
#                     }
# ```

# Would you like me to explain or break down this code?
# """

# print(extract_code_blocks(s))