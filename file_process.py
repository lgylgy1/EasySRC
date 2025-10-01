import os
from api import call_llm_api
from typing import Dict, Optional, Any, List
from init_project import config, logger, table, params
from filter_comment import filter_comment_from_code
from check_comment import filter_space

class FileProcess:
    file_path: str
    output_file_path: str
    lines: List[str]
    content: str
    generate_content: str
    generate_lines: List[str]
    unfind_lines: List[str]

    def __init__(self, file_path: str, content: str):
        self.file_path = file_path
        self.lines = content.split("\n")
        self.content = content
        self.output_file_path = os.path.join(params['output'], os.path.relpath(file_path, params['input'])) if params["input"]!=file_path else os.path.join(params['output'], os.path.basename(file_path))
        generate_content = ""
        self.unfind_lines = []
        for line in self.lines:
            if line.strip()!="":
                if line not in table:
                    self.unfind_lines.append(line)
                else:
                    generate_content+=table[line]+"\n"
            else:
                generate_content+=line+"\n"
        self.generate_content = generate_content if self.unfind_lines==[] else ""
        self.generate_lines = self.generate_content.split("\n")

    async def api_retry_and_update_table(self, retry_times: int = 5) -> None:
        """
        带重试地调用API，获取生成的注释，并更新generate_content、generate_lines、table、unfind_lines
        """
        global table
        prompt = f"路径:{self.file_path}的文件中包含如下代码：\n{self.content}\n请给出逐行详细注释后的代码，只给出带有注释的代码即可"
        for iii in range(retry_times):
            print(f"\n第{iii+1}次尝试调用API...")
            result = call_llm_api(config, prompt, system_prompt="你是一个优秀的软件工程师，能够准确、合理地为代码添加逐行详细中文注释（注释写在代码同行，只添加注释不修改代码、缩进与代码格式）。")
            if result.get("success"):
                if params['verbose']:
                    print("\nAPI调用成功：")
                    print("生成内容：", result["generated_content"])
                result["generated_content"] = result["generated_content"].strip()
                if result["generated_content"].startswith("```cpp\n") and result["generated_content"].endswith("\n```"):
                    result["generated_content"] = result["generated_content"][7:-4]
                self.generate_content = result["generated_content"]
                self.generate_lines = self.generate_content.split("\n")

                self.unfind_lines = []
                for line in self.lines:
                    if line.strip()=="":
                        continue
                    i=0
                    while i<len(self.generate_lines):
                        if line.strip().replace(" ", "") in self.generate_lines[i].strip().replace(" ", ""):
                            table[line]=self.generate_lines[i]
                            break
                        i+=1
                    if i==len(self.generate_lines):
                        print(f"未找到{line}对应的注释")
                        logger.error(f"file_path:{self.file_path},未找到{line}对应的注释")
                        self.unfind_lines.append(line)
                if self.unfind_lines==[] and filter_space(filter_comment_from_code(self.generate_content, os.path.splitext(self.file_path)[1].lower()))==filter_space(filter_comment_from_code(self.content, os.path.splitext(self.file_path)[1].lower())):
                    print("\n注释已全部生成完毕！")
                    break
        if result.get("error"):
            print("\nAPI调用失败：")
            print("错误信息：", result["error"])
            logger.error(f"API调用失败，错误信息：{result['error']}")
            if "detail" in result:
                logger.error(f"API调用失败，详细信息：{result['detail']}")
                print("详细信息：", result["detail"])


    async def output(self) -> bool:
        if self.unfind_lines==[] and filter_space(filter_comment_from_code(self.generate_content, os.path.splitext(self.file_path)[1].lower()))==filter_space(filter_comment_from_code(self.content, os.path.splitext(self.file_path)[1].lower())):
            os.makedirs(os.path.dirname(self.output_file_path), exist_ok=True)
            with open(self.output_file_path, "a", encoding="utf-8") as f:
                f.write(self.generate_content+"\n")
                return True
        else:
            return False

    async def process(self) -> bool:
        success = await self.output()
        if not success:
            await self.api_retry_and_update_table()
            success = await self.output()
        return success



