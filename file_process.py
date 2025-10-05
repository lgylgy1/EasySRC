import os
from api import call_llm_api
from typing import Dict, Optional, Any, List
from init_project import config, logger, table, params
from filter_comment import filter_comment_from_code
from check_comment import filter_space_and_comment, check_code_with_content, minDistance
from json_dict import save_dict_to_json
from extract_comment import extract_code_blocks

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
        print(f"初始化时未能从table中找到以下代码的注释：{self.unfind_lines}")

    async def api_retry_and_update_table(self, retry_times: int = 3) -> None:
        """
        带重试地调用API，获取生成的注释，并更新generate_content、generate_lines、table、unfind_lines
        """
        code_type = os.path.splitext(self.file_path)[1].lower()
        prompt = f"路径:{self.file_path}的文件中包含如下代码片段：\n{self.content}\n请给出逐行详细注释后的代码，只给出带有注释的代码即可，不要修改或删除代码片段的任何内容（因为是代码片段，所以可能有多余的括号，请不要删除多余的括号，也不要补充缺少的括号，确保删除注释后和源代码每行都相同），输出格式：```语言\n注释过的代码\n```。"
        for iii in range(retry_times):
            print(f"\n第{iii+1}次尝试调用API...")
            result = await call_llm_api(config, prompt, system_prompt="你是一个优秀的软件工程师，能够准确、合理地为代码片段添加逐行详细中文注释（注意：注释写在代码同行，只添加注释不修改任何代码、缩进与代码格式，不删除、添加注释之外的任何内容，确保删除注释后和源代码每行都相同）。记住：无论代码对错，你都不可以修改任何代码内容，只能添加注释")
            if result.get("success"):
                result["generated_content"] = extract_code_blocks(result["generated_content"])
                if len(result["generated_content"])!=1:
                    print(f"API调用成功，但API返回的代码块数量不为1，请检查API返回内容")
                    logger.error(f"API调用成功，但API返回的代码块数量不为1，请检查API返回内容")
                    ################输出内容被截断
                    self.generate_content = ""
                    self.generate_lines = []
                    self.unfind_lines = []
                    file_process=FileProcess(self.file_path, "\n".join(self.lines[:len(self.lines)//2]))
                    await file_process.api_retry_and_update_table()
                    self.generate_content += file_process.generate_content+"\n"
                    self.generate_lines.extend(file_process.generate_lines)
                    self.unfind_lines.extend(file_process.unfind_lines)
                    file_process=FileProcess(self.file_path, "\n".join(self.lines[len(self.lines)//2:]))
                    await file_process.api_retry_and_update_table()
                    self.generate_content += file_process.generate_content
                    self.generate_lines.extend(file_process.generate_lines)
                    self.unfind_lines.extend(file_process.unfind_lines)
                    return
                self.generate_content = result["generated_content"][0]
                self.generate_lines = self.generate_content.split("\n")
                self.unfind_lines = []
                generate_content = ""
                for line in self.lines:
                    if line.strip()=="":
                        continue
                    i=0
                    while i<len(self.generate_lines):
                        if check_code_with_content(line, self.generate_lines[i], code_type):
                            table[line]=self.generate_lines[i]
                            generate_content+=self.generate_lines[i]+"\n"
                            break
                        i+=1
                    if i==len(self.generate_lines):
                        # print(f"未找到{line}对应的注释")
                        logger.error(f"file_path:{self.file_path},未找到{line}对应的注释")
                        self.unfind_lines.append(line)
                        generate_content+=line+"\n"
                
                if self.unfind_lines==[]:    
                    print("\n注释已全部生成完毕！")
                    self.generate_content = generate_content
                    self.generate_lines = self.generate_content.split("\n")
                    break
                elif check_code_with_content(self.generate_content, self.content, code_type):
                    print("\n注释正确！")
                    for line in self.unfind_lines:
                        table[line]=""
                        for generate_line in self.generate_lines:
                            if filter_space_and_comment(generate_line, code_type) in filter_space_and_comment(line, code_type):
                                table[line]=table[line]+generate_line
                                if check_code_with_content(line, table[line], code_type):
                                    break
                    self.unfind_lines = []
                    break
                else:
                    print("\n未能找到以下注释：", self.unfind_lines)
                    logger.error(f"file_path:{self.file_path},未能找到以下注释：{self.unfind_lines}")
                    self.generate_content = generate_content
                    self.generate_lines = self.generate_content.split("\n")
                    if check_code_with_content(self.generate_content, self.content, code_type):
                        break
                    # minDistance(filter_space_and_comment(self.generate_content, code_type), filter_space_and_comment(self.content, code_type))

            if result.get("error"):
                print("\nAPI调用失败：")
                print("错误信息：", result["error"])
                logger.error(f"API调用失败，错误信息：{result['error']}")
                if "detail" in result:
                    logger.error(f"API调用失败，详细信息：{result['detail']}")
                    print("详细信息：", result["detail"])

    async def output(self) -> bool:
        code_type = os.path.splitext(self.file_path)[1].lower()
        if check_code_with_content(self.content, self.generate_content, code_type):
            os.makedirs(os.path.dirname(self.output_file_path), exist_ok=True)
            with open(self.output_file_path, "a", encoding="utf-8") as f:
                f.write(self.generate_content+"\n")
                return True
        else:
            if self.unfind_lines!=[]:
                print("\n未找到以下代码的注释：", self.unfind_lines)
            # minDistance(filter_space_and_comment(self.generate_content, code_type), filter_space_and_comment(self.content, code_type))  
            return False

    async def process(self) -> bool:
        success = await self.output()
        if not success:
            await self.api_retry_and_update_table()
            success = await self.output()
            if not success:
                print(f"{self.file_path}生成失败，将原文写入")
                logger.error(f"{self.file_path}生成失败，将原文写入")
                os.makedirs(os.path.dirname(self.output_file_path), exist_ok=True)
                with open(self.output_file_path, "a", encoding="utf-8") as f:
                    f.write(self.content+"\n")
        success = success and save_dict_to_json(table, "table.json")
        return success



