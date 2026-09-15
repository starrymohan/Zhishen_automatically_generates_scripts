import csv
import os

# TEMPLATE_DIR = '.'
TEMPLATE_DIR = './temple'
CSV_FILE = '启动跳闸弹窗.csv'
OUTPUT_BASE = '.'

PLACEHOLDERS = [f"1-{i}S" for i in range(1, 21)]

def pad_dpu(dpu):
    """补零至两位（用于 DPUNUM、DPUNNUM）"""
    return f"{int(dpu):02d}"

def pad_dpu_3(dpu):
    """补零至三位（用于 DPU3NUM）"""
    return f"{int(dpu):03d}"

def count_non_empty(row):
    return sum(1 for ph in PLACEHOLDERS if row.get(ph, '').strip())

def choose_template_size(count):
    if count <= 5:
        return 5
    elif count <= 15:
        return 15
    else:
        return 20

def read_text_file(filepath):
    """尝试多种编码读取文本文件"""
    encodings = ['utf-8-sig', 'utf-8', 'gb18030', 'gbk', 'gb2312', 'latin-1']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    # 保底
    with open(filepath, 'r', encoding='latin-1') as f:
        return f.read()

def write_text_file(filepath, content):
    """优先使用 gb2312，若失败则用 gb18030"""
    try:
        with open(filepath, 'w', encoding='gb2312', newline='\n') as f:
            f.write(content)
    except UnicodeEncodeError:
        print(f"警告：{filepath} 包含 gb2312 无法编码的字符，改用 gb18030")
        with open(filepath, 'w', encoding='gb18030', newline='\n') as f:
            f.write(content)

def replace_line(line, domain, title, dpu, sheet):
    dpu_padded_2 = pad_dpu(dpu)
    dpu_padded_3 = pad_dpu_3(dpu)

    # 通用占位符替换
    line = line.replace('DM', domain)
    line = line.replace('标  题', title)
    line = line.replace('DPUNNUM', dpu_padded_2)          # 两位
    line = line.replace('DPUNUM', dpu_padded_2)           # 两位（第二行也替换）
    line = line.replace('DPU3NUM', dpu_padded_3)          # 新增三位补零

    # 特殊组合占位符
    g_str = f"G{dpu_padded_2}P{sheet}PERMS"
    line = line.replace('GDPUNUMPSHEETNUMPERMS', g_str)

    return line

def replace_third_line(line, row):
    fields = line.split('\t')
    new_fields = []
    for f in fields:
        if f in PLACEHOLDERS:
            val = row.get(f, '').strip()
            new_fields.append(val if val else f)
        else:
            new_fields.append(f)
    return '\t'.join(new_fields)

def process_row(row, domain, dpu, sheet, device, action):
    cnt = count_non_empty(row)
    size = choose_template_size(cnt)
    # template_name = f"{action}弹窗{size}.gbw"
    template_name = f"{action}弹窗{size}.txt"
    template_path = os.path.join(TEMPLATE_DIR, template_name)

    try:
        content = read_text_file(template_path)
    except FileNotFoundError:
        print(f"警告：模板文件 {template_path} 不存在，跳过")
        return

    lines = content.splitlines()
    if len(lines) >= 2:
        lines[0] = replace_line(lines[0], domain, device, dpu, sheet)
        lines[1] = replace_line(lines[1], domain, device, dpu, sheet)
    if len(lines) >= 3:
        lines[2] = replace_third_line(lines[2], row)

    output_content = '\n'.join(lines)

    dpu_padded_2 = pad_dpu(dpu)
    suffix = '启动允许条件' if action == '启动' else '跳闸及首出'
    # filename = f"{dpu_padded_2}_{sheet}_{device}{suffix}.gbw"
    filename = f"{dpu_padded_2}_{sheet}_{device}{suffix}.txt"


    folder = os.path.join(OUTPUT_BASE, domain, dpu_padded_2)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    write_text_file(filepath, output_content)
    print(f"已生成：{filepath}")

def main():
    content = read_text_file(CSV_FILE)
    lines = content.splitlines()
    reader = csv.DictReader(lines)
    for row in reader:
        domain = row.get('域名', '').strip()
        dpu = row.get('DPU', '').strip()
        sheet = row.get('SHEET', '').strip()
        device = row.get('设备名称', '').strip()
        action = row.get('启动/跳闸', '').strip()
        if not all([domain, dpu, sheet, device, action]):
            print(f"跳过无效行：{row}")
            continue
        process_row(row, domain, dpu, sheet, device, action)

if __name__ == '__main__':
    main()