from file import read_files
from filter_comment import filter_comment_from_code
import os

def filter_space(content: str) -> str:
    return content.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", "").replace("\v", "").replace("\f", "")

def filter_space_and_comment(content: str, code_type: str) -> str:
    return filter_space(filter_comment_from_code(content, code_type))

def check_code(file_path: str, comment_path: str) -> bool:
    file=read_files(file_path)[file_path]
    comment=read_files(comment_path)[comment_path]
    file = filter_space("".join(file))
    comment = filter_space("".join(comment))
    if file==comment:
        return True
    else:
        # minDistance(comment[:10000], file[:10000])
        return False

def check_code_with_content(content: str, comment_content: str, code_type: str) -> bool:
    return filter_space_and_comment(content, code_type)==filter_space_and_comment(comment_content, code_type)

def minDistance(word1: str, word2: str) -> int:
    n1 = len(word1)
    n2 = len(word2)
    # 1. 初始化DP表，dp[i][j]表示word1[:i]到word2[:j]的最少编辑次数
    dp = [[0] * (n2 + 1) for _ in range(n1 + 1)]
    
    # 第一行：word1为空，需插入word2的所有字符
    for j in range(1, n2 + 1):
        dp[0][j] = dp[0][j-1] + 1
    # 第一列：word2为空，需删除word1的所有字符
    for i in range(1, n1 + 1):
        dp[i][0] = dp[i-1][0] + 1
    
    # 2. 填充DP表
    for i in range(1, n1 + 1):
        for j in range(1, n2 + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]  # 字符相同，无需操作
            else:
                # 字符不同，取“插入、删除、替换”的最小次数+1
                dp[i][j] = min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1]) + 1
    
    # 3. 反向回溯，提取具体编辑步骤
    edits = []
    i, j = n1, n2  # 从DP表右下角开始
    while i > 0 or j > 0:
        # 情况1：当前字符相同，无操作，回溯到左上角
        if i > 0 and j > 0 and word1[i-1] == word2[j-1]:
            i -= 1
            j -= 1
        # 情况2：当前字符不同，判断上一步操作
        else:
            # 优先判断“替换”（若dp[i][j]等于dp[i-1][j-1]+1）
            if i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
                edits.append(f"将 word1 第{i}个字符 '{word1[i-1]}' 替换为 word2 第{j}个字符 '{word2[j-1]}'")
                i -= 1
                j -= 1
            # 再判断“删除”（若dp[i][j]等于dp[i-1][j]+1）
            elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
                edits.append(f"删除 word1 第{i}个字符 '{word1[i-1]}'")
                i -= 1
            # 最后判断“插入”（若dp[i][j]等于dp[i][j-1]+1）
            elif j > 0 and dp[i][j] == dp[i][j-1] + 1:
                edits.append(f"在 word1 第{i+1}个位置插入 word2 第{j}个字符 '{word2[j-1]}'")
                j -= 1
    
    # 4. 输出结果：步骤反转（回溯是倒序，需转为正序）
    print("最少编辑次数：", dp[-1][-1])
    print("具体编辑步骤（从word1到word2）：")
    for idx, step in enumerate(reversed(edits), 1):
        print(f"{idx}. {step}")
    
    return dp[-1][-1]

# print(check_code(r"C:\Users\29853\Desktop\解读项目\MSVC-STL-14.44.35207 - 副本\agents.h", r"C:\Users\29853\Desktop\解读项目\MSVC-STL-14.44.35207 - 副本\README\agents.h"))

# file_name="\\algorithm"
# file_path=r"C:\Users\29853\Desktop\解读项目\MSVC-STL-14.44.35207 - 副本"+file_name
# comment_path=r"C:\Users\29853\Desktop\解读项目\MSVC-STL-14.44.35207 - 副本\README"+file_name
# file=read_files(file_path)[file_path]
# comment=read_files(comment_path)[comment_path]
# file = filter_space("".join(file))
# comment = filter_space("".join(comment))
# print(comment in file)
# print("comment len: ", len(comment), "file len: ", len(file))
# print(file.find(comment))

# for root, dirs, files in os.walk(r"C:\Users\29853\Desktop\解读项目\MSVC-STL-14.44.35207 - 副本\README"):
#     for file in files:
#         file_path = os.path.join(root, file)  # 拼接完整路径
#         if not check_code(file_path, file_path.replace("\\README", "")):
#             print(file_path)