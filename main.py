import os
import time
from config import Config
from file import read_files_by_extensions
from init_project import config, logger, table, params
from file_process import FileProcess
import asyncio
from typing import Dict, List
from json_dict import save_dict_to_json
from check_comment import check_code, check_code_with_content, filter_space_and_comment

async def split_file_and_process(file_path: str, file_content: List[str]) -> bool:
    start_time = time.strftime("%H:%M:%S")
    print(f"[{start_time}] 开始处理文件：{file_path}")
    content=""
    success=True
    for line in file_content:
        if ((len(content)>5000 and line!="" and line[0]!=" ") or (line=="" and len(content)>2500)) and content!="":
            file_process=FileProcess(file_path, content)
            success=await file_process.process() and success
            content=line+"\n" if line!="" else ""
        else:
            content+=(line+"\n")
    file_process=FileProcess(file_path, content)
    success=await file_process.process() and success
    end_time = time.strftime("%H:%M:%S")
    print(f"[{end_time}] 结束处理文件：{file_path}")
    return success

if __name__ == "__main__":
    if params['verbose']:
        print("\n开始处理...")
        print(f"输入路径: {params['input']}")
        print(f"输出路径: {params['output']}")
        print(f"详细日志: {'开启' if params['verbose'] else '关闭'}")
        print("配置信息：")
        print(config)
    
    files = read_files_by_extensions(params['input'], filter_comment=True)
    comment_files = read_files_by_extensions(params['output'], filter_comment=True)
    for file_path, content in files.items():
        code_type = os.path.splitext(file_path)[1].lower()
        comment_path=os.path.join(params['output'], os.path.relpath(file_path, params['input'])) if params["input"]!=file_path else os.path.join(params['output'], os.path.basename(file_path))
        if file_path in comment_files or (comment_path in comment_files and check_code_with_content("".join(content),"".join(comment_files[comment_path]), code_type)):
            print(f"文件{file_path}已处理或无需处理，跳过")
            continue
        elif comment_path in comment_files:
            text=""
            comment_content=filter_space_and_comment("".join(comment_files[comment_path]), code_type)
            comment_valid=False
            for i in range(len(content)):
                text+=filter_space_and_comment(content[i], code_type)
                if len(text)==len(comment_content) and text==comment_content:
                    success=asyncio.run(split_file_and_process(file_path, content[i+1:]))
                    comment_valid=True
                    break
            if not comment_valid:
                with open(comment_path, "w", encoding="utf-8") as f:
                    f.write("")
        else:
            success=asyncio.run(split_file_and_process(file_path, content))

    save_dict_to_json(table, "table.json")
    print("处理完成！")
    

 
