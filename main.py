import argparse
import sys
import os
from config import Config
from file import read_files_by_extensions,setup_logger
from api import call_llm_api
from json_dict import load_json_to_dict, save_dict_to_json

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

def process_content(file_path: str, content: str):
    need = False
    generate_content = ""
    for line1 in content.split("\n"):
        if line1.strip()!="":
            if line1 not in table:
                need = True
                break
            else:
                generate_content+=table[line1]+"\n"
        else:
            generate_content+=line1+"\n"
    if need:
        prompt = f"路径:{file_path}的文件中包含如下代码：\n{content}\n请给出逐行详细注释后的代码，只给出带有注释的代码即可"
        result = call_llm_api(config, prompt, system_prompt="你是一个优秀的软件工程师，能够准确、合理地为代码添加逐行详细中文注释（注释写在代码同行）。")
        if result.get("success"):
            if params['verbose']:
                print("\nAPI调用成功：")
                print("生成内容：", result["generated_content"])

            result["generated_content"] = result["generated_content"].strip()
            if result["generated_content"].startswith("```cpp\n") and result["generated_content"].endswith("\n```"):
                result["generated_content"] = result["generated_content"][7:-4]
            if params['input'] in file_path:
                output_file = file_path.replace(params['input'], params['output'])
            else:
                output_file = os.path.join(params['output'], os.path.basename(file_path))
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(result["generated_content"])
            generate_content = result["generated_content"].split("\n")
            j=0
            for line1 in content.split("\n"):
                if line1.strip()=="":
                    continue
                while(j<len(generate_content) and line1 not in generate_content[j]):
                    j+=1
                if j<len(generate_content):
                    table[line1]=generate_content[j]
                    j+=1
                else:
                    print(f"未找到{line1}对应的注释")
                    logger.error(f"未找到{line1}对应的注释")
        else:
            print("\nAPI调用失败：")
            print("错误信息：", result["error"])
            logger.error(f"API调用失败，错误信息：{result['error']}")
            if "detail" in result:
                logger.error(f"API调用失败，详细信息：{result['detail']}")
                print("详细信息：", result["detail"])
    else:
        if params['input'] in file_path:
            output_file = file_path.replace(params['input'], params['output'])
        else:
            output_file = os.path.join(params['output'], os.path.basename(file_path))
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(generate_content)

if __name__ == "__main__":
    # 获取完整参数
    params = get_command_line_args()
    config = Config()  # 实例化配置类
    
    if params['verbose']:
        print("\n开始处理...")
        print(f"输入路径: {params['input']}")
        print(f"输出路径: {params['output']}")
        print(f"详细日志: {'开启' if params['verbose'] else '关闭'}")
        print("配置信息：")
        print(config)
    
    logger = setup_logger()
    files = read_files_by_extensions(config, params['input'], filter_comment=False)
    print(f"共读取{len(files)}个文件")

    table = load_json_to_dict("table.json")

    for file_path, file_content in files.items():
        content=""
        for line in file_content:
            if ((len(content)>2500 and line[0]!=" ") or (line=="" and len(content)>1000)) and content!="":
                process_content(file_path, content)
                content=""
                continue
            content+=(line+"\n")
        process_content(file_path, content)
    save_dict_to_json(table, "table.json")
    print("处理完成！")
        
