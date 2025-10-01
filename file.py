import os
import logging
from typing import List, Dict
from config import Config
from encoding_detector import detect_file_encoding  # 导入编码检测函数
from filter_comment import filter_comment_from_code  # 导入注释过滤函数
from init_project import logger, config

def read_files_by_extensions(path: str, filter_comment: bool = True) -> Dict[str, List[str]]:
    """
    读取指定路径的内容（文件或文件夹），并将错误信息记录到日志
    
    参数:
        path: 待读取的文件或文件夹路径
        fliter_comment: 是否过滤掉注释行
    
    返回:
        字典，键为文件路径，值为文件内容（字符串）
        若有错误，返回包含错误信息的字典 {"error": "..."}，同时记录日志
    """
    # 检查路径是否存在
    if not os.path.exists(path):
        error_msg = f"路径不存在: {path}"
        logger.error(error_msg)  # 记录错误到日志
        return {"error": error_msg}
    
    # 检查是否有权限访问
    if not os.access(path, os.R_OK):
        error_msg = f"无权限访问: {path}"
        logger.error(error_msg)
        return {"error": error_msg}
    
    # 存储结果：{文件路径: 内容}
    result = {}
    
    # 1. 如果是文件，直接读取（需符合后缀要求）
    if os.path.isfile(path):
        # 获取文件后缀（如 ".txt"）
        file_ext = os.path.splitext(path)[1].lower()
        # 检查后缀是否在配置的 text_extensions 中（忽略大小写）
        allowed_extensions = [ext.lower() for ext in config.text_extensions]
        
        if file_ext in allowed_extensions:
            try:
                # 自动检测文件编码
                encoding = detect_file_encoding(path)
                if encoding == "unknown":
                    warning_msg = f"文件 {path} 编码未知，不进行读取"
                    logger.warning(warning_msg)  # 记录警告（非错误，但需要关注）
                
                with open(path, 'r', encoding=encoding, errors='replace') as f:
                    content = f.read()
                    if filter_comment:
                        content = filter_comment_from_code(content, file_ext)
                result[path] = content.split("\n")  # 以换行符分割为列表
                
            except UnicodeDecodeError as e:
                error_msg = f"文件 {path} 编码错误（{encoding}）：{str(e)}"
                logger.error(error_msg)
            except Exception as e:
                error_msg = f"文件 {path} 读取失败：{str(e)}"
                logger.error(error_msg)
        else:
            error_msg = f"文件 {path} 后缀不支持（{file_ext}），支持的后缀：{config.text_extensions}"
            logger.error(error_msg)
        
        return result
    
    # 2. 如果是文件夹，递归读取所有符合条件的文件
    elif os.path.isdir(path):
        try:
            # 遍历文件夹中的所有项
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                # 递归处理子文件夹或文件
                sub_result = read_files_by_extensions(item_path, filter_comment)
                # 合并结果（跳过错误信息，只保留文件内容）
                for key, value in sub_result.items():
                    if key != "error":
                        result[key] = value
        except Exception as e:
            error_msg = f"文件夹 {path} 遍历失败：{str(e)}"
            logger.error(error_msg)
        
        return result
    
    # 3. 既不是文件也不是文件夹（如特殊设备文件）
    else:
        error_msg = f"不支持的路径类型: {path}"
        logger.error(error_msg)
        return {}

def read_files(path: str, filter_comment: bool = True) -> Dict[str, List[str]]:
    """
    读取指定路径的内容（文件或文件夹），并将错误信息记录到日志
    
    参数:
        path: 待读取的文件或文件夹路径
        fliter_comment: 是否过滤掉注释行
    返回:
        字典，键为文件路径，值为文件内容（字符串）
        若有错误，返回包含错误信息的字典 {"error": "..."}，同时记录日志
    """
    # 检查路径是否存在
    if not os.path.exists(path):
        error_msg = f"路径不存在: {path}"
        logger.error(error_msg)  # 记录错误到日志
        return {"error": error_msg}
    # 检查是否有权限访问
    if not os.access(path, os.R_OK):
        error_msg = f"无权限访问: {path}"
        logger.error(error_msg)
        return {"error": error_msg}
    # 存储结果：{文件路径: 内容}
    result = {}
    # 1. 如果是文件，直接读取（需符合后缀要求）
    if os.path.isfile(path):
        try:
            # 自动检测文件编码
            encoding = detect_file_encoding(path)
            if encoding == "unknown":
                warning_msg = f"文件 {path} 编码未知，不进行读取"
                logger.warning(warning_msg)  # 记录警告（非错误，但需要关注）
            with open(path, 'r', encoding=encoding, errors='replace') as f:
                content = f.read()
                if filter_comment:
                    content = filter_comment_from_code(content, os.path.splitext(path)[1].lower())
            result[path] = content.split("\n")  # 以换行符分割为列表
        except UnicodeDecodeError as e:
            error_msg = f"文件 {path} 编码错误（{encoding}）：{str(e)}"
            logger.error(error_msg)
        except Exception as e:
            error_msg = f"文件 {path} 读取失败：{str(e)}"
            logger.error(error_msg)
        return result
    # 2. 如果是文件夹，递归读取所有符合条件的文件
    elif os.path.isdir(path):
        try:
            # 遍历文件夹中的所有项
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                # 递归处理子文件夹或文件
                sub_result = read_files(item_path, filter_comment)
                # 合并结果（跳过错误信息，只保留文件内容）
                for key, value in sub_result.items():
                    if key != "error":
                        result[key] = value
        except Exception as e:
            error_msg = f"文件夹 {path} 遍历失败：{str(e)}"
            logger.error(error_msg)
        return result
    # 3. 既不是文件也不是文件夹（如特殊设备文件）
    else:
        error_msg = f"不支持的路径类型: {path}"
        logger.error(error_msg)
        return {}


# 使用示例
#if __name__ == "__main__":
#    from config import Config  # 导入Config类
#    
#    try:
#        # 加载配置
#        config = Config()
#        print(f"支持的文件后缀: {config.text_extensions}")
#        
#        # 测试路径（可以是文件或文件夹）
#        test_path = "D:\\c++\\VS_project\\read_src"  # 替换为实际路径
#        
#        # 读取内容
#        files_content = read_files_by_extensions(config, test_path)
#        
#        # 处理结果
#        if "error" in files_content:
#            print(f"错误: {files_content['error']}")
#        else:
#            print(f"\n共读取 {len(files_content)} 个文件:")
#            for file_path, content in files_content.items():
#                print(f"\n--- {file_path} ---")
#                # 只显示前200个字符（避免内容过长）
#                print(content[:200] + ("..." if len(content) > 200 else ""))
#    
#    except Exception as e:
#        error_msg = f"执行失败: {str(e)}"
#        logger.error(error_msg)
#        print(error_msg)