import csv
import os

TEMPLATE_DIR = './temple'
CSV_FILE = '启动跳闸弹窗.csv'
OUTPUT_BASE = '.'

PLACEHOLDERS = [f"1-{i}S" for i in range(1, 21)]

def pad_dpu(dpu):
    return f"{int(dpu):02d}"

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
    """尝试多种编码读取文本文件，返回内容字符串"""
    encodings = ['utf-8-sig', 'utf-8', 'gb18030', 'gbk', 'gb2312', 'latin-1']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    # 保底：用 latin-1 不会出错（但可能有乱码）
    with open(filepath, 'r', encoding='latin-1') as f:
        return f.read()

def write_text_file(filepath, content):
    """尝试用 gb2312 写入，若失败则用 gb18030"""
    try:
        with open(filepath, 'w', encoding='gb2312', newline='\n') as f:
            f.write(content)
    except UnicodeEncodeError:
        print(f"警告：{filepath} 包含 gb2312 无法编码的字符，改用 gb18030")
        with open(filepath, 'w', encoding='gb18030', newline='\n') as f:
            f.write(content)

def replace_line(line, domain, title, dpu, sheet):
    dpu_padded = pad_dpu(dpu)
    line = line.replace('DM', domain)
    line = line.replace('标题', title)
    line = line.replace('DPUNNUM', dpu_padded)
    g_str = f"G{dpu_padded}P{sheet}PERMS"
    line = line.replace('GDPUNUMPSHEETNUMPERMS', g_str)
    line = line.replace('DPUNUM', dpu_padded)
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
    # template_name = f"{action}弹窗{size}.txt"
    template_name = f"{action}弹窗{size}.gbw"
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

    dpu_padded = pad_dpu(dpu)
    suffix = '启动允许条件' if action == '启动' else '跳闸及首出'
    # filename = f"{dpu_padded}_{sheet}_{device}{suffix}.txt"
    filename = f"{dpu_padded}_{sheet}_{device}{suffix}.gbw"

    folder = os.path.join(OUTPUT_BASE, domain, dpu_padded)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    write_text_file(filepath, output_content)
    print(f"已生成：{filepath}")

def main():
    # 读取 CSV 同样使用自动检测
    content = read_text_file(CSV_FILE)
    # 使用 csv 模块解析文本内容（需要按行分割）
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