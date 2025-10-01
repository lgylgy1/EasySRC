from file import read_files

def filter_space(content: str) -> str:
    return content.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", "").replace("\v", "").replace("\f", "")

def check_comment(file_path: str, comment_path: str) -> bool:
    file=read_files(file_path)[file_path]
    comment=read_files(comment_path)[comment_path]
    file = filter_space("".join(file))
    comment = filter_space("".join(comment))
    if file==comment:
        return True
    else:
        if len(file)!=len(comment):
            print(f"文件长度不匹配：{len(file)} vs {len(comment)}")
        for i in range(min(len(file),len(comment))):
            if file[i]!=comment[i]:
                print(f"第{i+1}个字符不匹配：{file[i]} vs {comment[i]}")
                print(f"文件内容：{file[i-30:i+30]}")
                print(f"注释内容：{comment[i-30:i+30]}")

# print(check_comment(r"C:\Users\29853\Desktop\解读项目\MSVC-STL-14.44.35207 - 副本\msclr\com\ptr.h",r"C:\Users\29853\Desktop\解读项目\MSVC-STL-14.44.35207 - 副本\msclr\com\README\ptr.h"))