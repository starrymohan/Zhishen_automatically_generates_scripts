import csv

def change_value(all_versions, num_versions, original_headers):
    # 存储所有版本的数组
    for j in range(1, num_versions + 1):
        version_headers = []
        for field in original_headers:
            if field:
                version_headers.append(field + str(j+10))
            else:
                version_headers.append(field)
        all_versions.append(version_headers)   # 保存到数组
    # print(all_versions)
    # [['INPUTA11', 'INPUTB11', 'OUTPUTA11', 'OUTPUTB11', ''],
    # ['INPUTA12', 'INPUTB12', 'OUTPUTA12', 'OUTPUTB12', '']]

def print_change(change, be_change, read_change):
    # 字符串是不可变对象，函数内部的 read_change = read_change.replace(...)
    # 只是让局部变量 read_change 指向了一个新字符串，并不会修改外部的 read_change10to10。
    # 因此调用 print_change 后，外部的 read_change10to10 仍然是原始模板内容，
    # 看起来像是“被释放了”，实际上只是没有被更新。
    result = read_change[:]
    for x in range(len(be_change)-1):
        for j in range(2):
            # 确保标题存在且替换值非空
            if change[x][j] and be_change[x+1][j]:
                result = result.replace(change[x][j], be_change[x+1][j])
    return result

# 读取 CSV 获取有效行数
be_change = []
with open("模拟量仿真数据.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:#将启对启数组存入valid_row_data,后面用于替换
        be_change.append(row)
print(be_change)

# 读取标题行
with open("模拟量仿真数据.csv", "r") as f:
    ls = f.read().splitlines()
original_headers = ls[0].strip().split(",")
# original_headers = ['INPUTA', 'INPUTB', 'OUTPUTA', 'OUTPUTB', '']

num_versions10to10 = len(be_change)

change = []

change_value(change, num_versions10to10, original_headers)

read_change = []

#读取被替换部分
# [['INPUTA11', 'INPUTB11', 'OUTPUTA11', 'OUTPUTB11', ''],
# ['INPUTA12', 'INPUTB12', 'OUTPUTA12', 'OUTPUTB12', ''],
# ['INPUTA13', 'INPUTB13', 'OUTPUTA13', 'OUTPUTB13', ''],
# 。。。
with open("模拟量V1.txt","r") as f:
    readed10to10=f.read()
    read_change = readed10to10[:]

read_change = print_change(change, be_change, readed10to10)

# 写入文件
if (len(be_change)):
    with open("out10to10.txt", "w", encoding="utf-8") as f:
        f.write(read_change)

#观察一个类型生成了几个
print("模拟量：", len(be_change)-1)
print("打印完成")