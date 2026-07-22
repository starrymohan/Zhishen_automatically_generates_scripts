import csv

# 读取符合条件的行
valid_rows_data = []
with open("仿真数据V1.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        non_empty = sum(1 for field in row if field.strip() != "")
        if non_empty == 4:
            valid_rows_data.append(row)

# 读取原始标题行
with open("仿真数据V1.csv", "r") as f:
    ls = f.read().splitlines()
original_headers = ls[0].strip().split(",")

num_versions = len(valid_rows_data)
all_headers_versions = []
for j in range(1, num_versions + 1):
    new_headers = [f"{field}{j}" if field else "" for field in original_headers]
    all_headers_versions.append(new_headers)

# 读取模板
with open("启对启V2.txt", "r", encoding="utf-8") as f:
    template = f.read()

# 处理每一行
version_idx = 0
for line in ls[1:]:
    changed = line.strip().split(",")
    # 条件：INPUTA 非空，INPUTB 空，OUTPUTA 非空，OUTPUTB 空
    if changed[0] and not changed[1] and changed[2] and not changed[3]:
        current_headers = all_headers_versions[version_idx]
        result = template
        for x in range(len(current_headers)):
            # 只替换非空的占位符，并且被替换值也非空
            if current_headers[x] and changed[x]:
                result = result.replace(current_headers[x], changed[x])
        print(result)
        version_idx += 1
# import csv
#
# # 读取 CSV，存储符合条件的行
# valid_rows_data = []
#
# with open("仿真数据V1.csv", "r") as f:
#     reader = csv.reader(f)
#     for row in reader:
#         non_empty = sum(1 for field in row if field.strip() != "")
#         if non_empty == 4:
#             valid_rows_data.append(row)
#
# # 读取原始标题行
# with open("仿真数据V1.csv", "r") as f:
#     ls = f.read().splitlines()
# original_headers = ls[0].strip().split(",")
#
# num_versions = len(valid_rows_data)
# all_headers_versions = []  # 存储所有版本
#
# # # 生成最后一个版本的标题（这里只保留了最后一个 j 的结果，若需要全部版本需另行存储）
# # for j in range(1, num_versions + 1):
# #     new_headers = []
# #     for field in original_headers:
# #         if field:
# #             new_headers.append(field + str(j))
# #         else:
# #             new_headers.append(field)
# # print(new_headers)
#
# for j in range(1, num_versions + 1):
#     new_headers = []
#     for field in original_headers:
#         if field:
#             new_headers.append(field + str(j))
#         else:
#             new_headers.append(field)
#     all_headers_versions.append(new_headers)  # 保存当前版本
#
# # 查看所有版本
# for idx, headers in enumerate(all_headers_versions, start=1):
#     print(f"版本{idx}: {headers}")
#
# # 读取替换模板
# with open("启对启V1.txt", "r", encoding="utf-8") as f:
#     readed10to10 = f.read()
#
# # 处理每一行数据（从第2行开始）
# version_idx = 0
# for line in ls[1:]:
#     changed = line.strip().split(",")
#     if changed[0] and not changed[1] and changed[2] and not changed[3]:
#         current_headers = all_headers_versions[version_idx]
#         read = readed10to10[:]
#         for x in range(len(current_headers)):
#             if current_headers[x]:
#                 read = read.replace(current_headers[x], changed[x])
#         print(read)
#         version_idx += 1
# # 处理每一行数据（从第2行开始）
# for line in ls[1:]:
#     changed = line.strip().split(",")
#     # 判断条件：第一个非空，第二个空，第三个非空，第四个空
#     if changed[0] and not changed[1] and changed[2] and not changed[3]:
#         # 复制模板内容
#         read = readed10to10[:]
#         # 进行替换
#         for x in range(len(new_headers)):
#             if new_headers[x]:
#                 read = read.replace(new_headers[x], changed[x])
#         #print(read)
#     else:
#         # 如果不满足条件，也许不处理或打印原内容？这里简单跳过
#         pass
'''
import csv

# 读取 CSV，存储符合条件的行（本例未使用，仅用于获取版本数量）
valid_rows_data = []
with open("仿真数据V1.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        non_empty = sum(1 for field in row if field.strip() != "")
        if non_empty == 4:
            valid_rows_data.append(row)

# 读取原始标题行
with open("仿真数据V1.csv", "r") as f:
    ls = f.read().splitlines()
original_headers = ls[0].strip().split(",")  # 例如 ['INPUTA','INPUTB','OUTPUTA','OUTPUTB','']

# 决定生成多少个版本（例如按照 valid_rows_data 的行数，或者手动指定）
num_versions = len(valid_rows_data)  # 假设每个符合条件的行对应一个版本
# 如果希望固定生成 1~5，可以改为 num_versions = 5

# 生成并打印每个版本
for j in range(1, num_versions + 1):   # j 从 1 开始
    new_headers = []
    for field in original_headers:
        if field:                     # 非空字段加数字
            new_headers.append(field + str(j))
        else:                         # 空字段保持空字符串
            new_headers.append(field)
    # print(new_headers)

with open("启对启V1.txt", "r", encoding="utf-8") as f:
    readed10to10 = f.read()

for line in ls[1:]:
    changed=line.strip().split(",")
    if(changed[0] and not changed[1] and changed[2] and not changed[3]):
        read=readed10to10[:]

    for x in range(0,len(new_headers)):
        if(new_headers[x]):
            read=read.replace(new_headers[x],changed[x])
    print(read)


with open("仿真数据.csv","r") as f:
   ls=f.read().splitlines()

with open("启对启V1.txt","r") as f:
   readed10to10=f.read()
   
be_change = ls[0].strip().split(",")

#替换题头    
j = 1

for i in range(len(be_change)):
   if be_change[i]:                     # 跳过空字符串
       be_change[i] += str(j)       # 将 int 转为 str 再拼接
       if (i+1) % 4 == 0:
           j += 1

#替换题头
with open("仿真数据.csv","r") as f:
   ls=f.read().splitlines()

with open("启停对启停.txt","r") as f:
   readed11to11=f.read()

be_change = ls[0].strip().split(",")

j = 1

for i in range(len(be_change)):
   if be_change[i]:                     # 跳过空字符串
       be_change[i] += str(j)       # 将 int 转为 str 再拼接
       if (i+1) % 4 == 0:
           j += 1

print(be_change)
'''

'''
valid_row_numbers = []  # 存储符合条件行号

with open("仿真数据V1.csv", "r") as f:
    reader = csv.reader(f)
    for row_num, row in enumerate(reader, start=1):
        non_empty = sum(1 for field in row if field.strip() != "")
        if non_empty == 5:
            valid_row_numbers.append(row_num)   # 存储行号

print("非空字段=5的行号：", valid_row_numbers)
# 例如：[2, 7, 8] 表示第2、7、8行
'''
'''


for line in ls[1:]:
    changed=line.strip().split(",")
    if(changed[0] and changed[1] and changed[2] and changed[3]):
        read=readed11to11[:]

    for x in range(0, len(be_change)):
        if (be_change[x]):
            read = read.replace(be_change[x], changed[x])

        # print(changed[4])
    print(read)

with open("启停对启.txt","r") as f:
    readed11to10=f.read()

with open("启停对停.txt","r") as f:
    readed11to01=f.read()

with open("启对启停.txt","r") as f:
    readed10to11=f.read()

with open("启对启.txt","r") as f:
    readed10to10=f.read()

with open("启对停.txt","r") as f:
    readed10to01=f.read()

with open("停对启停.txt","r") as f:
    readed01to11=f.read()

with open("停对启.txt","r") as f:
    readed01to10=f.read()

with open("停对停.txt","r") as f:
    readed01to01=f.read()


be_change = ls[0].strip().split(",")
for line in ls[1:]:
    changed=line.strip().split(",")
    if(changed[0] and changed[1] and changed[2] and changed[3]):
        read=readed11to11[:]
    elif(changed[0] and changed[1] and changed[2] and not changed[3]):
        read=readed11to10[:]
    elif(changed[0] and changed[1] and not changed[2] and changed[3]):
        read=readed11to01[:]
    elif(changed[0] and not changed[1] and changed[2] and changed[3]):
        read=readed10to11[:]
    elif(changed[0] and not changed[1] and changed[2] and not changed[3]):
        read=readed10to10[:]
    elif(changed[0] and not changed[1] and not changed[2] and changed[3]):
        read=readed10to01[:]
    elif(not changed[0] and changed[1] and changed[2] and changed[3]):
        read=readed01to11[:]
    elif(not changed[0] and changed[1] and changed[2] and not changed[3]):
        read=readed01to10[:]
    elif(not changed[0] and changed[1] and not changed[2] and changed[3]):
        read=readed01to01[:]
    elif((not changed[0] and not changed[1]) or (not changed[2] and not changed[3])):
        continue

    for x in range(0,len(be_change)):
        if(be_change[x]):
            read=read.replace(be_change[x],changed[x])

    #print(changed[4])
    print(read)

# 读取所有文件（略，保持不变）...

with open("output.txt", "w", encoding="utf-8") as f:
    # 写入表头
    #f.write("第五字段|处理后文本\n")

    be_change = ls[0].strip().split(",")
    for line in ls[1:]:
        changed = line.strip().split(",")
        if len(changed) < 5:
            continue

        c0, c1, c2, c3 = changed[0], changed[1], changed[2], changed[3]
        if c0 and c1 and c2 and c3:
            read = readed11to11[:]
        elif c0 and c1 and c2 and not c3:
            read = readed11to10[:]
        elif c0 and c1 and not c2 and c3:
            read = readed11to01[:]
        elif c0 and not c1 and c2 and c3:
            read = readed10to11[:]
        elif c0 and not c1 and c2 and not c3:
            read = readed10to10[:]
        elif c0 and not c1 and not c2 and c3:
            read = readed10to01[:]
        elif not c0 and c1 and c2 and c3:
            read = readed01to11[:]
        elif not c0 and c1 and c2 and not c3:
            read = readed01to10[:]
        elif not c0 and c1 and not c2 and c3:
            read = readed01to01[:]
        elif (not c0 and not c1) or (not c2 and not c3):
            continue
        else:
            continue

        # 替换占位符
        for x in range(len(be_change)):
            if be_change[x]:
                read = read.replace(be_change[x], changed[x])

        # 写入一行
        f.write(f"{read}\n")

print("处理完成，结果已保存到 output.txt")

'''