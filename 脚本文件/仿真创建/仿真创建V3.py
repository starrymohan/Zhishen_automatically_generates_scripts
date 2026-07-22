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
    for x in range(len(be_change)):
        for j in range(4):
            # 确保标题存在且替换值非空
            if change[x][j] and be_change[x][j]:
                result = result.replace(change[x][j], be_change[x][j])
    return result

# 读取 CSV 获取有效行数
be_change10to01 = []
be_change10to10 = []
be_change10to11 = []
be_change11to01 = []
be_change11to10 = []
be_change11to11 = []
be_change11to10 = []
be_change01to01 = []
be_change01to10 = []
be_change01to11 = []
with open("仿真数据V1.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:#将启对启数组存入valid_row_data,后面用于替换
        if (row[0] and not row[1] and not row[2] and  row[3]):
            be_change10to01.append(row)
        elif (row[0] and not row[1] and row[2] and not row[3]):
            be_change10to10.append(row)
        elif (row[0] and not row[1] and row[2] and row[3]):
            be_change10to11.append(row)
        elif (row[0] and row[1] and not row[2] and row[3]):
            be_change11to01.append(row)
        elif (row[0] and row[1] and row[2] and not row[3]):
            be_change11to10.append(row)
        elif (row[0] and row[1] and row[2] and row[3]):
            be_change11to11.append(row)
        if (not row[0] and row[1] and not row[2] and  row[3]):
            be_change01to01.append(row)
        elif (not row[0] and row[1] and row[2] and not row[3]):
            be_change01to10.append(row)
        elif (not row[0] and row[1] and row[2] and row[3]):
            be_change01to11.append(row)

# 读取标题行
with open("仿真数据V1.csv", "r") as f:
    ls = f.read().splitlines()
original_headers = ls[0].strip().split(",")
# original_headers = ['INPUTA', 'INPUTB', 'OUTPUTA', 'OUTPUTB', '']

num_versions = len(be_change10to01)
num_versions10to01 = len(be_change10to01)
num_versions10to10 = len(be_change10to10)
num_versions10to11 = len(be_change10to11)
num_versions11to01 = len(be_change11to01)
num_versions11to10 = len(be_change11to10)
num_versions11to11 = len(be_change11to11)
num_versions01to01 = len(be_change01to01)
num_versions01to10 = len(be_change01to10)
num_versions01to11 = len(be_change01to11)

# change = []
change10to01 = []
change10to10 = []
change10to11 = []
change11to01 = []
change11to10 = []
change11to11 = []
change11to10 = []
change01to01 = []
change01to10 = []
change01to11 = []
change_value(change10to01, num_versions10to01, original_headers)
change_value(change10to10, num_versions10to10, original_headers)
change_value(change10to11, num_versions10to11, original_headers)
change_value(change11to01, num_versions11to01, original_headers)
change_value(change11to10, num_versions11to10, original_headers)
change_value(change11to11, num_versions11to11, original_headers)
change_value(change01to01, num_versions01to01, original_headers)
change_value(change01to10, num_versions01to10, original_headers)
change_value(change01to11, num_versions01to11, original_headers)
# change_value(change, num_versions, original_headers)

read_change01to01 = []
read_change01to10 = []
read_change01to11 = []
read_change10to01 = []
read_change10to10 = []
read_change10to11 = []
read_change11to01 = []
read_change11to10 = []
read_change11to11 = []

#读取被替换部分
# [['INPUTA11', 'INPUTB11', 'OUTPUTA11', 'OUTPUTB11', ''],
# ['INPUTA12', 'INPUTB12', 'OUTPUTA12', 'OUTPUTB12', ''],
# ['INPUTA13', 'INPUTB13', 'OUTPUTA13', 'OUTPUTB13', ''],
# 。。。
with open("启对停V1.txt","r") as f:
    readed10to01=f.read()
    read_change10to01 = readed10to01[:]
with open("启对启V2.txt","r") as f:
    readed10to10=f.read()
    read_change10to10 = readed10to10[:]
with open("启对启停V1.txt","r") as f:
    readed10to11=f.read()
    read_change10to11 = readed10to11[:]
with open("启停对停V1.txt","r") as f:
    readed11to01=f.read()
    read_change11to01 = readed11to01[:]
with open("启停对启V1.txt","r") as f:
    readed11to10=f.read()
    read_change11to10 = readed11to10[:]
with open("启停对启停V1.txt","r") as f:
    readed11to11=f.read()
    read_change11to11 = readed11to11[:]
with open("停对停V1.txt","r") as f:
    readed01to01=f.read()
    read_change01to01 = readed01to01[:]
with open("停对启V1.txt","r") as f:
    readed01to10=f.read()
    read_change01to10 = readed01to10[:]
with open("停对启停V1.txt","r") as f:
    readed01to11=f.read()
    read_change01to11 = readed01to11[:]

read_change01to01 = print_change(change01to01, be_change01to01, readed01to01)
read_change01to10 = print_change(change01to10, be_change01to10, readed01to10)
read_change01to11 = print_change(change01to11, be_change01to11, readed01to11)
read_change10to01 = print_change(change10to01, be_change10to01, readed10to01)
read_change10to10 = print_change(change10to10, be_change10to10, readed10to10)
read_change10to11 = print_change(change10to11, be_change10to11, readed10to11)
read_change11to01 = print_change(change11to01, be_change11to01, readed11to01)
read_change11to10 = print_change(change11to10, be_change11to10, readed11to10)
read_change11to11 = print_change(change11to11, be_change11to11, readed11to11)

# 写入文件
if(len(be_change01to01)):
    with open("out01to01.txt", "w", encoding="utf-8") as f:
        f.write(read_change01to01)
if (len(be_change01to10)):
    with open("out01to10.txt", "w", encoding="utf-8") as f:
        f.write(read_change01to10)
if (len(be_change01to11)):
    with open("out01to11.txt", "w", encoding="utf-8") as f:
        f.write(read_change01to11)
if (len(be_change10to01)):
    with open("out10to01.txt", "w", encoding="utf-8") as f:
        f.write(read_change10to01)
if (len(be_change10to10)):
    with open("out10to10.txt", "w", encoding="utf-8") as f:
        f.write(read_change10to10)
if (len(be_change10to11)):
    with open("out10to11.txt", "w", encoding="utf-8") as f:
        f.write(read_change10to11)
if (len(be_change11to01)):
    with open("out11to01.txt", "w", encoding="utf-8") as f:
        f.write(read_change11to01)
if (len(be_change11to10)):
    with open("out11to10.txt", "w", encoding="utf-8") as f:
        f.write(read_change11to10)
if (len(be_change11to11)):
    with open("out11to11.txt", "w", encoding="utf-8") as f:
        f.write(read_change11to11)

#观察一个类型生成了几个
print("启对停：", len(be_change10to01))
print("启对启：", len(be_change10to10))
print("启对启停：", len(be_change10to11))
print("启停对停：", len(be_change11to01))
print("启停对启：", len(be_change11to10))
print("启停对启停：", len(be_change11to11))
print("停对停：", len(be_change01to01))
print("停对启：", len(be_change01to10))
print("停对启停：", len(be_change01to11))
print("打印完成")