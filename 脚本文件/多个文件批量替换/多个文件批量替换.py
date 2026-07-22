import csv
import os


def parse_csv_data(filepath: str) -> list:
    """解析PID逻辑生成.csv文件"""
    records = []

    for enc in ['gb2312', 'gbk', 'gb18030', 'utf-8-sig', 'utf-8']:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                reader = csv.reader(f)

                # 跳过第一行（占位符行）
                next(reader)

                for row in reader:
                    if len(row) >= 12:  # 确保有足够的字段
                        record = {
                            'SHEETNAME': row[0].strip(),
                            'OUTNAME': row[1].strip(),
                            'INNAME': row[2].strip(),
                            'DPUNUM': row[3].strip(),
                            'SHEETNUM': row[4].strip(),
                            'MLNAME': row[5].strip(),
                            'MANAME': row[6].strip(),
                            'MAOUT': row[7].strip(),
                            'SETSP': row[8].strip(),
                            'SETPV': row[9].strip(),
                            'MAAUTO': row[10].strip(),
                            'MAGP': row[11].strip()
                        }
                        records.append(record)

                print(f"使用编码 {enc} 成功读取，共{len(records)}条记录")
                return records
        except UnicodeDecodeError:
            continue

    raise ValueError("无法识别CSV文件的编码")


def read_template(filepath: str) -> str:
    """读取SHEETNAME.TXT模板文件"""
    for enc in ['gb2312', 'gbk', 'gb18030', 'utf-8-sig', 'utf-8']:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read().strip()
        except UnicodeDecodeError:
            continue
    raise ValueError("无法识别模板文件的编码")


def replace_template(template: str, record: dict) -> str:
    """替换模板中的占位符"""
    result = template

    # 按顺序替换所有占位符
    replacements = [
        ('OUTNAME', record['OUTNAME']),
        ('INNAME', record['INNAME']),
        ('DPUNUM', record['DPUNUM']),
        ('SHEETNUM', record['SHEETNUM']),
        ('MLNAME', record['MLNAME']),
        ('MANAME', record['MANAME']),
        ('MAOUT', record['MAOUT']),
        ('SETSP', record['SETSP']),
        ('SETPV', record['SETPV']),
        ('MAAUTO', record['MAAUTO']),
        ('MAGP', record['MAGP']),
    ]

    for placeholder, value in replacements:
        result = result.replace(placeholder, value)

    return result


def write_file_safe(filepath: str, content: str) -> None:
    """安全写入文件"""
    encodings = ['gbk', 'gb18030', 'utf-8']
    for enc in encodings:
        try:
            with open(filepath, 'w', encoding=enc) as f:
                f.write(content)
            return
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    # 文件路径
    csv_file = "PID逻辑生成.csv"
    template_file = "SHEETNAME.cbp"
    base_output_dir = "output"

    # 读取数据
    records = parse_csv_data(csv_file)
    if not records:
        print("错误：未读取到任何数据")
        return

    template = read_template(template_file)

    print(f"模板内容: {template}")
    print(f"共找到 {len(records)} 条记录")
    print("-" * 80)

    # 显示第一条记录的数据
    if records:
        print("第一条记录数据：")
        for key, value in records[0].items():
            print(f"  {key}: {value}")
        print("-" * 80)

    # 统计各DPUNUM
    dpu_stats = {}
    for record in records:
        dpu_num = record['DPUNUM']
        dpu_stats[dpu_num] = dpu_stats.get(dpu_num, 0) + 1

    print("按DPUNUM分组：")
    for dpu_num in sorted(dpu_stats.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        print(f"  DPU{dpu_num} → {dpu_stats[dpu_num]}个文件")
    print("-" * 80)

    # 验证第一条记录的替换结果
    if records:
        first_record = records[0]
        expected_result = "K0PBN10AP001XQ01，K0PBN10AP001YQ01，19内幕20统一A19ML020A哦A19MA020A、A19MA020AO\tA19M020SP\tA19M020PV\tD19M020_AUTO\tG19P020MRE"

        actual_result = replace_template(template, first_record)

        print("验证第一条记录：")
        print(f"  文件名: {first_record['SHEETNAME']}.TXT")
        print(f"  替换结果: {actual_result}")
        print(f"  预期结果: {expected_result}")
        print(f"  匹配: {'✓' if actual_result == expected_result else '✗'}")

        if actual_result != expected_result:
            print("\n差异分析：")
            print(f"  结果长度: {len(actual_result)}, 预期长度: {len(expected_result)}")
            for i, (a, e) in enumerate(zip(actual_result, expected_result)):
                if a != e:
                    print(f"  位置{i}: 实际'{a}' vs 预期'{e}'")
                    if i > 200:  # 只显示前200个差异
                        print("  ... (后续差异省略)")
                        break
        print("-" * 80)

    # 逐条处理
    success_count = 0
    fail_count = 0

    for i, record in enumerate(records, 1):
        try:
            # 创建DPU文件夹
            dpu_num = record['DPUNUM']
            dpu_folder = f"DPU{dpu_num}"
            output_dir = os.path.join(base_output_dir, dpu_folder)
            os.makedirs(output_dir, exist_ok=True)

            # 替换模板
            content = replace_template(template, record)

            # 生成文件名
            filename = f"{record['SHEETNAME']}.cbp"
            output_path = os.path.join(output_dir, filename)

            # 写入文件
            write_file_safe(output_path, content)

            print(f"[{i}/{len(records)}] ✓ {dpu_folder}/{filename}")
            success_count += 1

        except Exception as e:
            print(f"[{i}/{len(records)}] ✗ 错误: {str(e)}")
            fail_count += 1

    print("-" * 80)
    print(f"处理完成！成功: {success_count}, 失败: {fail_count}")

    # 显示文件结构
    print(f"\n文件结构 ({base_output_dir}/):")
    for dpu_num in sorted(dpu_stats.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        folder = f"DPU{dpu_num}"
        folder_path = os.path.join(base_output_dir, folder)
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if f.endswith('.TXT')]
            print(f"  ├── {folder}/ ({len(files)}个文件)")
            # 显示前3个文件名
            for file in files[:3]:
                print(f"  │   ├── {file}")
            if len(files) > 3:
                print(f"  │   └── ... 还有 {len(files) - 3} 个文件")


if __name__ == "__main__":
    main()