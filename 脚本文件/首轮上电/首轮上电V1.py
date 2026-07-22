#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import sys

# ---------- 配置 ----------
CSV_FILE = "文本替换值.csv"
TEMPLATE_DIR = "cb"
FIELD_DOMAIN = "DM"
FIELD_STATION = "DPUNUM"
SPECIAL_TEMPLATE = "DPUDPUNUM首轮上电点表.csv"  # 需要特殊存放目录的模板
SPECIAL_OUTPUT_DIR = "首轮上电电表"              # 特殊模板的输出子目录名
# -------------------------

def get_template_files():
    """获取模板文件夹下的所有文件"""
    files = []
    if not os.path.isdir(TEMPLATE_DIR):
        print(f"错误：模板目录 '{TEMPLATE_DIR}' 不存在。")
        sys.exit(1)
    for fname in os.listdir(TEMPLATE_DIR):
        full = os.path.join(TEMPLATE_DIR, fname)
        if os.path.isfile(full):
            files.append(full)
    if not files:
        print(f"错误：在 '{TEMPLATE_DIR}' 下未找到任何模板文件。")
        sys.exit(1)
    return files

def read_file_with_fallback(file_path):
    """尝试以 GB2312 读取，若失败则用 UTF-8"""
    for encoding in ('gb2312', 'utf-8'):
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"无法解码文件：{file_path}")

def safe_write_file(file_path, content):
    """安全写入文件：若文件被占用尝试删除，否则抛出异常"""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except PermissionError:
            raise PermissionError(f"文件 '{file_path}' 被其他程序占用，请关闭后重试。")
    with open(file_path, 'w', encoding='gb2312', newline='\n') as f:
        f.write(content)

def process_row(row, template_files):
    """处理单行 CSV 记录，针对每个模板生成输出文件"""
    domain = row.get(FIELD_DOMAIN, '').strip()
    station_raw = row.get(FIELD_STATION, '').strip()
    if not domain or not station_raw:
        print(f"警告：行 {row} 缺少域号或站号，已跳过。")
        return

    try:
        station_int = int(station_raw)
        station_padded_3 = f"{station_int:03d}"   # 用于drop文件夹名
        station_padded_2 = f"{station_int:02d}"   # 用于文件名和内容替换
    except ValueError:
        print(f"警告：站号 '{station_raw}' 不是有效数字，行 {row} 已跳过。")
        return

    dpnum_val = station_int
    dpubignum_val = dpnum_val + 60

    # 提前创建域目录（如果不存在），但具体子目录在每个模板内创建
    # 为简化，在循环内创建具体目录

    for template_path in template_files:
        template_basename = os.path.basename(template_path)
        try:
            template_content = read_file_with_fallback(template_path)
        except Exception as e:
            print(f"读取模板 {template_basename} 失败：{e}，跳过。")
            continue

        # ---- 替换所有列占位符 ----
        content = template_content
        for col, val in row.items():
            if col and val is not None:
                if col == FIELD_STATION:
                    content = content.replace(col, station_padded_2)
                else:
                    content = content.replace(col, val)

        # ---- DPUBIGNUM ----
        content = content.replace("DPUBIGNUM", str(dpubignum_val))

        # ---- 特殊模板的额外处理：,0 -> , ----
        if template_basename == SPECIAL_TEMPLATE:
            content = content.replace(",0", ",")

        # ---- 生成目标文件名 ----
        target_filename = template_basename.replace("DPUNUM", station_padded_2)

        # ---- 决定目标目录 ----
        if template_basename == SPECIAL_TEMPLATE:
            # 特殊模板放在 {域号}/首轮上电电表/
            target_dir = os.path.join(domain, SPECIAL_OUTPUT_DIR)
        else:
            # 其他模板放在 {域号}/drop{三位站号}/
            target_dir = os.path.join(domain, f"drop{station_padded_3}")

        os.makedirs(target_dir, exist_ok=True)
        output_path = os.path.join(target_dir, target_filename)

        # ---- 安全写入 ----
        try:
            safe_write_file(output_path, content)
            print(f"已生成：{output_path}")
        except PermissionError as e:
            print(f"错误：{e}，跳过文件 {target_filename}")
        except Exception as e:
            print(f"写入 {output_path} 时发生意外错误：{e}，跳过。")

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