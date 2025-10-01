import os
from config import Config
from file import read_files_by_extensions
from init_project import config, logger, table, params
from file_process import FileProcess
import asyncio
from typing import Dict
from json_dict import save_dict_to_json

async def split_file_and_process(file_path: str, file_content: str) -> bool:
    content=""
    success=True
    for line in file_content:
        if ((len(content)>5000 and line[0]!=" ") or (line=="" and len(content)>2500)) and content!="":
            file_process=FileProcess(file_path, content)
            success=await file_process.process() and success
            content=""
        else:
            content+=(line+"\n")
    file_process=FileProcess(file_path, content)
    success=await file_process.process() and success
    return success

async def process_file_with_semaphore(file_path: str, file_content: str, semaphore: asyncio.Semaphore) -> bool:
    """通过信号量控制并发的文件处理函数"""
    async with semaphore:  # 限制并发数
        return await split_file_and_process(file_path, file_content)


async def main_process(files: Dict[str, str], max_concurrent: int = 5):
    """并发处理所有文件，控制最大并发数"""
    # 创建信号量，限制最大并发数为 5
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # 创建所有任务（不立即执行）
    tasks = [
        process_file_with_semaphore(file_path, content, semaphore)
        for file_path, content in files.items()
    ]
    
    # 并发执行所有任务，等待全部完成
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    if params['verbose']:
        print("\n开始处理...")
        print(f"输入路径: {params['input']}")
        print(f"输出路径: {params['output']}")
        print(f"详细日志: {'开启' if params['verbose'] else '关闭'}")
        print("配置信息：")
        print(config)
    
    files = read_files_by_extensions(params['input'], filter_comment=True)
    print(f"共读取{len(files)}个文件，将以最大并发数 5 处理")

    # 运行并发处理主函数
    # asyncio.run(main_process(files, max_concurrent=5))
    for file_path, content in files.items():
        success=asyncio.run(split_file_and_process(file_path, content))

    save_dict_to_json(table, "table.json")
    print("处理完成！")
    

 
