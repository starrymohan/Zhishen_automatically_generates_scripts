'''
import os

documentname = []
def read_with_os_listdir(folder_path):
    """使用os.listdir读取文件夹内文件（非递归）"""
    print("\n使用os.listdir读取:")
    for filename in os.listdir(folder_path):
        name_without_ext = os.path.splitext(filename)[0]
        documentname = name_without_ext.split('_', 1)[1] if '_' in name_without_ext else name_without_ext
        # file_path = os.path.join(folder_path, filename)
        # # if os.path.isfile(file_path):
        #     # print(f"文件: {file_path}")
        # documentname = filename.split('_', 1)[1]
        # print(documentname)

read_with_os_listdir(".\drop001")


import os

def read_with_os_listdir(folder_path):
    """使用os.listdir读取文件夹内文件（非递归），返回提取的字符串列表"""
    result_list = []  # 局部列表，用于存储每个文件的提取结果
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):  # 只处理文件，忽略子文件夹
            name_without_ext = os.path.splitext(filename)[0]
            if '_' in name_without_ext:
                document_part = name_without_ext.split('_', 1)[1]
            else:
                document_part = name_without_ext
            result_list.append(document_part)
            # print(document_part)
    return result_list

# 调用函数并接收返回值
extracted_parts = read_with_os_listdir("drop001")
print("\n函数外部获取到的列表:", extracted_parts)

# 如果需要访问单个元素
for part in extracted_parts:
    print(part)
'''

import os

def process_files(source_dir, output_dir):
    """
    遍历 source_dir 中的每个文件：
      - 提取文件名中第一个下划线之后、扩展名之前的部分作为替换词
      - 读取文件内容（尝试 gb2312/gbk 编码），将所有“设备”替换为该替换词
      - 将修改后的内容以 GB2312 编码写入 output_dir
    """
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        if not os.path.isfile(file_path):
            continue

        # 1. 获取替换词：第一个下划线后、扩展名前的内容
        name_without_ext = os.path.splitext(filename)[0]
        if '_' in name_without_ext:
            replace_str = name_without_ext.split('_', 1)[1]
        else:
            replace_str = name_without_ext

        # 2. 读取原始文件内容（优先 gb2312，若失败则使用 gbk）
        try:
            with open(file_path, 'r', encoding='gb2312') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()

        # 3. 替换所有“设备”为 replace_str
        new_content = content.replace('equipment', replace_str)

        # 4. 以 GB2312 编码写入输出文件夹
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='gb2312') as f:
            f.write(new_content)

        print(f"处理完成：{filename} -> 将“设备”替换为“{replace_str}”，输出编码 GB2312")

if __name__ == '__main__':
    source_folder = "./drop001"      # 存放原始文件的文件夹
    target_folder = "./processed"    # 用于存放替换后文件的新文件夹
    process_files(source_folder, target_folder)