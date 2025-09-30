import os
import chardet  # 需安装：pip install chardet


def detect_file_encoding(file_path: str, sample_size: int = 1024 * 1024) -> str:
    """
    检测文本文件的编码方式（基于chardet，支持更多编码且准确性更高）
    
    参数:
        file_path: 文本文件路径
        sample_size: 读取的样本大小（字节），默认1MB（平衡准确性和性能）
    
    返回:
        推测的编码方式（如"utf-8"、"gbk"、"windows-1252"等），失败则返回"unknown"
    """
    # 1. 基础校验：文件是否存在且可读取
    if not os.path.exists(file_path):
        print(f"错误：文件不存在 - {file_path}")
        return "unknown"
    if not os.path.isfile(file_path):
        print(f"错误：不是文件 - {file_path}")
        return "unknown"
    if not os.access(file_path, os.R_OK):
        print(f"错误：无读取权限 - {file_path}")
        return "unknown"
    
    # 2. 读取文件样本（避免读取过大文件，提高效率）
    try:
        with open(file_path, 'rb') as f:
            # 读取前sample_size字节，若文件更小则读取全部
            sample = f.read(sample_size)
    except Exception as e:
        print(f"读取文件失败：{str(e)}")
        return "unknown"
    
    if not sample:  # 空文件无法检测
        return "unknown"
    
    # 3. 优先检测带BOM的编码（chardet可能误判BOM编码）
    # UTF-8 BOM (0xEF 0xBB 0xBF)
    if sample.startswith(b'\xef\xbb\xbf'):
        return 'utf-8-sig'
    # UTF-16 LE BOM (0xFF 0xFE)
    if sample.startswith(b'\xff\xfe'):
        return 'utf-16le'
    # UTF-16 BE BOM (0xFE 0xFF)
    if sample.startswith(b'\xfe\xff'):
        return 'utf-16be'
    # UTF-32 LE BOM (0xFF 0xFE 0x00 0x00)
    if sample.startswith(b'\xff\xfe\x00\x00'):
        return 'utf-32le'
    # UTF-32 BE BOM (0x00 0x00 0xFE 0xFF)
    if sample.startswith(b'\x00\x00\xfe\xff'):
        return 'utf-32be'
    
    # 4. 使用chardet检测编码（支持更多编码类型）
    try:
        # 检测样本的编码，返回字典（包含'encoding'和'confidence'等键）
        detection_result = chardet.detect(sample)
        encoding = detection_result.get('encoding')
        confidence = detection_result.get('confidence', 0.0)
        
        # 过滤低置信度结果（置信度低于0.5的编码可靠性差）
        if encoding and confidence >= 0.5:
            # 标准化部分编码名称（chardet可能返回"GB2312"，统一为"gbk"等）
            encoding = encoding.lower()
            if encoding == 'gb2312':
                return 'gbk'  # GBK兼容GB2312，优先返回更通用的GBK
            if encoding == 'iso-8859-1':
                # 很多情况下iso-8859-1会被误判，优先尝试windows-1252（兼容且更常见）
                return 'windows-1252'
            return encoding
        else:
            # 低置信度时返回常见备选编码
            print(f"编码检测置信度低（{confidence}），无法确定")
            return "unknown"
    except Exception as e:
        print(f"chardet检测失败：{str(e)}")
        return "unknown"


# 使用示例
# if __name__ == "__main__":
#     test_files = [
#         "test_utf8.txt",
#         "test_utf8_bom.txt",
#         "test_gbk.txt",
#         "test_big5.txt",  # 繁体中文编码，chardet支持更好
#         "test_windows1252.txt"
#     ]
    
#     for file in test_files:
#         if os.path.exists(file):
#             encoding = detect_file_encoding(file)
#             print(f"文件 {file} 的编码推测为: {encoding}")
#         else:
#             print(f"文件 {file} 不存在")