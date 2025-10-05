def filter_comment_from_code(code: str, code_type: str) -> str:
    """
    过滤代码中的注释，支持多种编程语言
    
    参数:
        code: 原始代码字符串
        code_type: 代码文件后缀（如 ".py", ".js", ".java", ".html" 等）
    
    返回:
        移除注释后的代码字符串
    """
    # 根据文件类型选择对应的注释处理逻辑
    if code_type == ".py":
        return _filter_python_comment(code)
    elif code_type in (".js", ".java", ".c", ".cpp", ".h", ".hpp", ".c++", ""):
        return _filter_c_style_comment(code)
    elif code_type == ".html":
        return _filter_html_comment(code)
    else:
        # 不支持的类型，返回原始代码
        return code


def _filter_python_comment(code: str) -> str:
    """过滤 Python 注释（# 单行注释、多行注释）"""
    lines = code.split('\n')
    result = []
    in_multiline = False  # 是否在多行注释中
    multiline_delim = None  # 多行注释分隔符（''' 或 """）
    
    for line in lines:
        i = 0
        n = len(line)
        new_line = []
        
        while i < n:
            if in_multiline:
                # 查找多行注释结束符
                if line.startswith(multiline_delim, i):
                    in_multiline = False
                    i += len(multiline_delim)
                else:
                    i += 1
            else:
                # 单行注释 #
                if line.startswith('#', i):
                    break  # 忽略 # 后的内容
                # 多行注释开始（''' 或 """）
                elif line.startswith('"""', i):
                    in_multiline = True
                    multiline_delim = '"""'
                    i += 3
                elif line.startswith("'''", i):
                    in_multiline = True
                    multiline_delim = "'''"
                    i += 3
                else:
                    new_line.append(line[i])
                    i += 1
        
        result.append(''.join(new_line))
    
    return '\n'.join(result)


def _filter_c_style_comment(code: str) -> str:
    """过滤 C 风格注释（// 单行注释、/* */ 多行注释），适用于 JS/Java/C/C++"""
    lines = code.split('\n')
    result = []
    in_multiline = False  # 是否在 /* */ 多行注释中
    
    for line in lines:
        i = 0
        n = len(line)
        new_line = []
        
        while i < n:
            if in_multiline:
                # 查找多行注释结束符 */
                if i + 1 < n and line[i] == '*' and line[i+1] == '/':
                    in_multiline = False
                    i += 2  # 跳过 */
                else:
                    i += 1
            else:
                # 单行注释 //
                if i + 1 < n and line[i] == '/' and line[i+1] == '/':
                    break  # 忽略 // 后的内容
                # 多行注释开始 /*
                elif i + 1 < n and line[i] == '/' and line[i+1] == '*':
                    in_multiline = True
                    i += 2  # 跳过 /*
                else:
                    new_line.append(line[i])
                    i += 1
        
        result.append(''.join(new_line))
    
    return '\n'.join(result)


def _filter_html_comment(code: str) -> str:
    """过滤 HTML 注释（<!-- -->，支持跨多行）"""
    lines = code.split('\n')
    result = []
    in_comment = False  # 是否在 <!-- --> 注释中
    
    for line in lines:
        i = 0
        n = len(line)
        new_line = []
        
        while i < n:
            if in_comment:
                # 查找注释结束符 -->
                if i + 2 < n and line[i] == '-' and line[i+1] == '-' and line[i+2] == '>':
                    in_comment = False
                    i += 3  # 跳过 -->
                else:
                    i += 1
            else:
                # 查找注释开始符 <!--
                if i + 3 < n and line[i] == '<' and line[i+1] == '!' and line[i+2] == '-' and line[i+3] == '-':
                    in_comment = True
                    i += 4  # 跳过 <!--
                else:
                    new_line.append(line[i])
                    i += 1
        
        result.append(''.join(new_line))
    
    return '\n'.join(result)

# # 测试 Python 注释过滤
# py_code = """
# x = 10  # 单行注释
# y = 20

# '''
# 多行注释第一行
# 多行注释第二行
# '''
# print(x + y)
# """
# print("Python 过滤后：")
# print(filter_comment_from_code(py_code, ".py"))
# print("-" * 50)

# # 测试 JavaScript 注释过滤
# js_code = """
# let a = 5; // 单行注释
# /*
# 多行注释
# 跨两行
# */
# console.log(a);
# """
# print("JavaScript 过滤后：")
# print(filter_comment_from_code(js_code, ".js"))
# print("-" * 50)

# # 测试 HTML 注释过滤
# html_code = """
# <html>
# <!-- 头部注释 -->
# <head>
#     <title>测试</title>
# </head>
# <body>
#     <!-- 主体注释
#     跨多行 -->
#     <p>内容</p>
# </body>
# </html>
# """
# print("HTML 过滤后：")
# print(filter_comment_from_code(html_code, ".html"))