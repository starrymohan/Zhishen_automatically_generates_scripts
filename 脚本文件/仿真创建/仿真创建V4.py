import csv

# ============================================================
# 1. 配置：CSV 列名 -> 模板占位符
# ============================================================
COL_TO_PLACEHOLDER = {
    "DM":   "DM",
    "DPU":  "DPUNUM",
    "启动": "INPUTA",
    "停止": "INPUTB",
    "已启": "OUTPUTA",
    "已停": "OUTPUTB",
}

# 布尔条件用到的 4 列（对应原 INPUTA/INPUTB/OUTPUTA/OUTPUTB 的判断）
BOOL_COLS = ["启动", "停止", "已启", "已停"]

# 替换顺序：先长后短，避免 DM 误伤 DPUNUM 等
REPLACE_ORDER = ["DPUNUM", "INPUTA", "INPUTB", "OUTPUTA", "OUTPUTB", "DM"]


# ============================================================
# 2. 函数定义
# ============================================================
def change_value(all_versions, num_versions):
    """为每个版本生成占位符字典列表。
    例如：[{'DM': 'DM11', 'DPUNUM': 'DPUNUM11', 'INPUTA': 'INPUTA11', ...}, ...]
    """
    for j in range(1, num_versions + 1):
        version_headers = {}
        for placeholder in COL_TO_PLACEHOLDER.values():
            version_headers[placeholder] = placeholder + str(j + 10)
        all_versions.append(version_headers)


def print_change(change, be_change, read_change, col_index):
    """按占位符替换模板内容。
    change[x]     : 第 x 行对应的占位符字典
    be_change[x]  : 第 x 行的 CSV 原始数据
    read_change   : 模板字符串
    col_index     : {列名: 索引}
    """
    result = read_change[:]
    for x in range(len(be_change)):
        row = be_change[x]
        mapping = change[x]
        # 先长后短，避免 DM 误伤 DPUNUM
        for placeholder in REPLACE_ORDER:
            # 占位符名 -> CSV 列名（反向查找）
            col_name = None
            for cn, ph in COL_TO_PLACEHOLDER.items():
                if ph == placeholder:
                    col_name = cn
                    break
            if col_name is None:
                continue
            value = row[col_index[col_name]]
            if mapping.get(placeholder) and value != "":
                result = result.replace(mapping[placeholder], str(value))
    return result


# def load_template(path):
#     with open(path, "r", encoding="utf-8") as f:
#         return f.read()
import chardet
def detect_encoding(path):
    with open(path, "rb") as f:
        raw = f.read(100000)
    return chardet.detect(raw)["encoding"]

def load_template(path):
    enc = detect_encoding(path)
    # chardet 有时会返回 None 或 ASCII，做个兜底
    if not enc or enc.lower() == "ascii":
        enc = "utf-8"
    with open(path, "r", encoding=enc) as f:
        return f.read()

# ============================================================
# 3. 读取 CSV，按启停组合分类
# ============================================================
be_change10to01 = []
be_change10to10 = []
be_change10to11 = []
be_change11to01 = []
be_change11to10 = []
be_change11to11 = []
be_change01to01 = []
be_change01to10 = []
be_change01to11 = []

import chardet

def detect_encoding(path):
    with open(path, "rb") as f:
        raw = f.read(100000)          # 只读前 100KB 足够判断
    return chardet.detect(raw)["encoding"]

csv_encoding = detect_encoding("文本替换值.csv")
print("检测到编码：", csv_encoding)

# with open("文本替换值.csv", "r", encoding="utf-8-sig") as f:
#     reader = csv.reader(f)
with open("文本替换值.csv", "r", encoding=csv_encoding) as f:
    reader = csv.reader(f)
    headers = next(reader)                          # 第一行是列名
    col_index = {name.strip(): i for i, name in enumerate(headers)}

    # 检查必需列是否存在
    for col in BOOL_COLS + list(COL_TO_PLACEHOLDER.keys()):
        if col not in col_index:
            raise KeyError(f"CSV 缺少列：{col}，实际列名：{headers}")

    i_qd = col_index["启动"]   # INPUTA
    i_zt = col_index["停止"]   # INPUTB
    i_yq = col_index["已启"]   # OUTPUTA
    i_yt = col_index["已停"]   # OUTPUTB

    for row in reader:
        if len(row) < len(headers):
            continue                                # 跳过不完整行

        a = row[i_qd].strip()
        b = row[i_zt].strip()
        c = row[i_yq].strip()
        d = row[i_yt].strip()

        # 启动、停止、已启、已停 四列的 0/1 组合
        if a and not b and not c and d:
            be_change10to01.append(row)
        elif a and not b and c and not d:
            be_change10to10.append(row)
        elif a and not b and c and d:
            be_change10to11.append(row)
        elif a and b and not c and d:
            be_change11to01.append(row)
        elif a and b and c and not d:
            be_change11to10.append(row)
        elif a and b and c and d:
            be_change11to11.append(row)

        if not a and b and not c and d:
            be_change01to01.append(row)
        elif not a and b and c and not d:
            be_change01to10.append(row)
        elif not a and b and c and d:
            be_change01to11.append(row)


# ============================================================
# 4. 为每种类型生成占位符版本
# ============================================================
change10to01, change10to10, change10to11 = [], [], []
change11to01, change11to10, change11to11 = [], [], []
change01to01, change01to10, change01to11 = [], [], []

change_value(change10to01, len(be_change10to01))
change_value(change10to10, len(be_change10to10))
change_value(change10to11, len(be_change10to11))
change_value(change11to01, len(be_change11to01))
change_value(change11to10, len(be_change11to10))
change_value(change11to11, len(be_change11to11))
change_value(change01to01, len(be_change01to01))
change_value(change01to10, len(be_change01to10))
change_value(change01to11, len(be_change01to11))


# ============================================================
# 5. 读取模板
# ============================================================
templates = {
    "10to01": load_template("启对停V1.txt"),
    "10to10": load_template("启对启V2.txt"),
    "10to11": load_template("启对启停V1.txt"),
    "11to01": load_template("启停对停V1.txt"),
    "11to10": load_template("启停对启V1.txt"),
    "11to11": load_template("启停对启停V1.txt"),
    "01to01": load_template("停对停V1.txt"),
    "01to10": load_template("停对启V1.txt"),
    "01to11": load_template("停对启停V1.txt"),
}


# ============================================================
# 6. 执行替换
# ============================================================
outputs = {
    "10to01": print_change(change10to01, be_change10to01, templates["10to01"], col_index),
    "10to10": print_change(change10to10, be_change10to10, templates["10to10"], col_index),
    "10to11": print_change(change10to11, be_change10to11, templates["10to11"], col_index),
    "11to01": print_change(change11to01, be_change11to01, templates["11to01"], col_index),
    "11to10": print_change(change11to10, be_change11to10, templates["11to10"], col_index),
    "11to11": print_change(change11to11, be_change11to11, templates["11to11"], col_index),
    "01to01": print_change(change01to01, be_change01to01, templates["01to01"], col_index),
    "01to10": print_change(change01to10, be_change01to10, templates["01to10"], col_index),
    "01to11": print_change(change01to11, be_change01to11, templates["01to11"], col_index),
}


# ============================================================
# 7. 写文件
# ============================================================
for key, content in outputs.items():
    if content.strip():                             # 有内容才写
        filename = f"out{key}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"已写入 {filename}")


# ============================================================
# 8. 统计
# ============================================================
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