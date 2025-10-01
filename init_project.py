import os
from config import Config
from json_dict import load_json_to_dict
import argparse
import logging

# 配置日志系统
def setup_logger():
    """初始化    配置日志记录器，将错误信息写入日志文件
    日志格式：时间 - 级别 - 消息
    """
    # 日志文件路径（与脚本同目录下的 logs 文件夹）
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)  # 确保日志目录存在
    log_file = os.path.join(log_dir, "file_reader.log")
    
    # 创建日志记录器
    logger = logging.getLogger("FileReader")
    logger.setLevel(logging.DEBUG)  # 只记录错误级别及以上的日志
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    
    # 定义日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    
    return logger


def get_command_line_args():
    """
    解析命令行参数，若参数不完整则提示用户补充输入
    返回完整的参数字典
    """
    # 1. 定义命令行参数解析器
    parser = argparse.ArgumentParser(description="示例：处理命令行参数并自动补全")
    # 添加需要的参数（nargs='?' 表示可选，不填则为None）
    parser.add_argument("-i","--input", nargs='?', help="输入文件路径（必填）")
    parser.add_argument("-o","--output", nargs='?', help="输出文件路径（必填）")
    # parser.add_argument("--mode", nargs='?', help="处理模式（可选，默认：normal）", default="normal")
    parser.add_argument("-v","--verbose", action="store_true", help="是否显示详细日志（可选）")
    # 2. 解析命令行参数
    args = parser.parse_args()
    args_dict = vars(args)  # 转换为字典，方便处理
    # 3. 定义必填参数列表（根据实际需求修改）
    required_args = ["input", "output"]
    # 4. 检查必填参数是否完整，不完整则提示用户输入
    for arg in required_args:
        if args_dict[arg] is None or args_dict[arg].strip() == "":
            # 循环提示，直到用户输入有效内容
            while True:
                user_input = input(f"请输入 {arg}（必填）: ").strip()
                if user_input:
                    args_dict[arg] = user_input
                    break
                print(f"错误：{arg} 不能为空，请重新输入！")
    return args_dict

config = Config()
logger = setup_logger()
table = load_json_to_dict("table.json")
params = get_command_line_args()