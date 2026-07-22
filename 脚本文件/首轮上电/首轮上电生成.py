#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import sys
import glob

# ---------- 配置 ----------
CSV_FILE = "文本替换值.csv"
TEMPLATE_DIR = "cb"
FIELD_DOMAIN = "DM"
FIELD_STATION = "DPUNUM"
# -------------------------

def get_template_files():
    pattern = os.path.join(TEMPLATE_DIR, "*.cbp")
    files = glob.glob(pattern)
    if not files:
        print(f"错误：在 '{TEMPLATE_DIR}' 下未找到任何 .cbp 模板文件。")
        sys.exit(1)
    return files

def read_file_with_fallback(file_path):
    for encoding in ('gb2312', 'utf-8'):
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"无法解码文件：{file_path}")

def process_row(row, template_files):
    domain = row.get(FIELD_DOMAIN, '').strip()
    station_raw = row.get(FIELD_STATION, '').strip()
    if not domain or not station_raw:
        print(f"警告：行 {row} 缺少域号或站号，已跳过。")
        return

    try:
        station_int = int(station_raw)
        station_padded_3 = f"{station_int:03d}"   # 用于文件夹名（drop+三位）
        station_padded_2 = f"{station_int:02d}"   # 用于文件名和内容替换（两位）
    except ValueError:
        print(f"警告：站号 '{station_raw}' 不是有效数字，行 {row} 已跳过。")
        return

    dpnum_val = station_int
    dpubignum_val = dpnum_val + 60

    # 目标目录：{域号}/drop{三位站号}/
    target_dir = os.path.join(domain, f"drop{station_padded_3}")
    os.makedirs(target_dir, exist_ok=True)

    for template_path in template_files:
        template_basename = os.path.basename(template_path)
        template_content = read_file_with_fallback(template_path)

        # ---- 替换内容 ----
        content = template_content
        for col, val in row.items():
            if col and val is not None:
                # 特殊处理：如果列名是 DPUNUM，用两位补零的值替换
                if col == FIELD_STATION:
                    content = content.replace(col, station_padded_2)
                else:
                    content = content.replace(col, val)

        # 特殊处理 DPUBIGNUM
        content = content.replace("DPUBIGNUM", str(dpubignum_val))

        # ---- 生成文件名：将模板文件名中的 DPUNUM 替换为两位补零 ----
        target_filename = template_basename.replace("DPUNUM", station_padded_2)

        # ---- 写入文件 ----
        output_path = os.path.join(target_dir, target_filename)
        with open(output_path, 'w', encoding='gb2312', newline='\n') as f:
            f.write(content)

        print(f"已生成：{output_path}")

def main():
    if not os.path.isfile(CSV_FILE):
        print(f"错误：CSV 文件 '{CSV_FILE}' 不存在。")
        sys.exit(1)

    template_files = get_template_files()
    print(f"找到模板文件：{', '.join(map(os.path.basename, template_files))}")

    try:
        with open(CSV_FILE, 'r', encoding='gb2312') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except UnicodeDecodeError:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    if not rows:
        print("CSV 文件为空或没有数据行。")
        return

    for row in rows:
        process_row(row, template_files)

    print("\n所有记录处理完毕。")

if __name__ == "__main__":
    main()