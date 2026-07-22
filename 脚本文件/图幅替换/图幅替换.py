import os
# old_str = []
# 读取被替换图幅（要查找的旧内容）
with open('被替换图幅.txt', 'r', encoding='utf-8') as f:
    old_str = f.read()
# new_str = []
# 读取替换图幅（要替换成的新内容）
with open('替换图幅.txt', 'r', encoding='utf-8') as f:
    new_str = f.read()
# print(new_str)
# 读取被替换文件（待处理的文件）
with open('被替换文件.txt', 'r', encoding='utf-8') as f:   # 根据文件实际编码调整，这里原文件声明为GB2312
    content = f.read()

# 执行全部替换
new_content = content.replace(old_str, new_str)

# 将结果写回原文件（或新文件）
with open('替换后的文件.txt', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("替换完成！")


