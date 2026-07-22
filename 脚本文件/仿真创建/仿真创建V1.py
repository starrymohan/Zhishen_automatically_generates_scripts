import csv

# 读取 CSV 获取有效行数
valid_rows_data = []
with open("仿真数据V1.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if(row[0] and not row[1] and row[2] and not row[3]):
            valid_rows_data.append(row)#将启对启数组存入valid_row_data,后面用于替换

print(valid_rows_data)
# 读取标题行
with open("仿真数据V1.csv", "r") as f:
    ls = f.read().splitlines()
original_headers = ls[0].strip().split(",")

print(original_headers)

num_versions = len(valid_rows_data)

# 存储所有版本的数组
all_versions = []

for j in range(1, num_versions + 1):
    version_headers = []
    for field in original_headers:
        if field:
            version_headers.append(field + str(j+10))
        else:
            version_headers.append(field)
    all_versions.append(version_headers)   # 保存到数组

print(all_versions)

# with open("仿真数据.csv","r") as f:
#     ls=f.read().splitlines()

with open("启对启V1.txt","r", encoding="utf-8") as f:
    readed10to10=f.read()#['INPUTA1', 'INPUTB1', 'OUTPUTA1', 'OUTPUTB1', '']
    read = readed10to10[:]

# be_change = ls[0].strip().split(",")#['INPUTA', 'INPUTB', 'OUTPUTA', 'OUTPUTB', '']
# for line in ls[1:]:
#     changed = line.strip().split(",")#仿真数据读取 #['J0LDP40AH003YB02', '', 'J0LDP40AH003XB02_SIM', '', '']
#     print(changed)

for x in range(0,len(valid_rows_data)):
    for j in range(4):
        if(valid_rows_data[x]):
            read = read.replace(all_versions[x][j], valid_rows_data[x][j])
# 写入文件
with open("out.txt", "w", encoding="utf-8") as f:
    f.write(read)

print(read)