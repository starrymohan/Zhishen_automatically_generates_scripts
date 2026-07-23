#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
import pandas as pd
from io import StringIO

# ---------- 配置 ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(SCRIPT_DIR, "待替换文件")
TEMPLATE_DIR = os.path.join(SCRIPT_DIR, "template")

# 测点列名（中文）
POINT_COLS = ["启动", "停止", "已启", "已停", "故障", "远方"]
# 关键信息列名（CSV中实际列名）
KEY_COLS = ["域名", "DPU", "SHEET", "设备名称", "驱动级"]

# ---------- 映射关系（CSV列名 → 模板占位符） ----------
MAPPING = {
    "DM": "DM",
    "DPU": "DROPNUM",
    "启动": "INPUT1",
    "停止": "INPUT2",
    "已启": "OUTPUT1",
    "已停": "OUTPUT2",
    "SHEET": "SHEETNUM",
    "设备名称": "equipment",
    "CUSTOM": "CUSTOM",      # 特殊生成
    "GPA": "GPA",            # 特殊生成
    "GPB": "GPB",            # 特殊生成
    "故障": "ERR",           # 直接取值
    "远方": "NOSPOT",        # 直接取值
    "就地": "SPOT"           # 直接取值
}

# ---------- 辅助函数 ----------
def is_valid(value):
    """判断测点值是否有效（非空且不等于 '#N/A' 或 '#/A'）"""
    if pd.isna(value):
        return False
    if isinstance(value, str):
        v = value.strip()
        if v == "" or v.upper() in ["#N/A", "#/A"]:
            return False
    return True

def get_point_status(row):
    """从行数据中提取各个测点的有效性"""
    status = {}
    for col in POINT_COLS:
        status[col] = is_valid(row.get(col))
    return status

def determine_template(driver_level, row):
    """
    根据驱动级和测点存在情况选择模板文件名
    返回模板文件名（字符串），若无法确定则返回 None
    """
    dl = str(driver_level).strip()
    s = get_point_status(row)
    has_start  = s["启动"]
    has_stop   = s["停止"]
    has_started = s["已启"]
    has_stopped = s["已停"]
    has_fault  = s["故障"]
    has_remote = s["远方"]

    if dl == "5":
        if has_start and has_stop and has_started and has_stopped:
            if not has_fault and not has_remote:
                return "MOV.txt"
            elif has_fault and not has_remote:
                return "MOV_ERR.txt"
            elif not has_fault and has_remote:
                return "MOV_NOT.txt"
            elif has_fault and has_remote:
                return "MOV_NOT_ERR.txt"
        return None

    elif dl == "6":
        # 新规则：根据基本测点组合选择模板，远方/故障的存在与否不影响模板选择
        if has_start and has_stop and has_started and has_stopped:
            return "MOTORII_NOT_ERR.txt"
        elif has_start and has_stop and has_started:
            return "MOTORII_NOT_ERR_1DI.txt"
        elif has_start and has_started:
            return "MOTORII _1DO_NOT_ERR_1DI.txt"
        else:
            return None

    elif dl == "7":
        return "BREAKERII_NOT_ERR.txt"

    elif dl == "9":
        if has_start and has_stop and has_started and has_stopped:
            if not has_fault and not has_remote:
                return "SCSOV.txt"
            if has_remote and not has_fault:
                return "SCSOV_NOT.txt"
        if has_start and not has_stop and not has_started and not has_stopped and not has_remote:
            return "SCSOV_1DO.txt"
        return None

    elif dl == "11":
        return "MOVSPII_NOT_ERR.txt"

    else:
        return None

def build_output_path(domain, station, sheet, device_name):
    """构建输出目录和文件名"""
    dir_path = os.path.join(str(domain), str(station))
    filename = f"SH{sheet}_{device_name}.cbp"
    return dir_path, filename

def read_csv_with_encoding(filepath):
    """
    增强的 CSV 读取：先以二进制读取，尝试多种编码解码，再用 pandas 解析
    """
    with open(filepath, 'rb') as f:
        raw = f.read()

    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']
    for enc in encodings:
        try:
            text = raw.decode(enc)
            df = pd.read_csv(StringIO(text), header=0, dtype=str)
            if df.shape[1] > 1:
                return df
        except Exception:
            continue
    raise ValueError(f"无法使用常见编码读取 {filepath}，请检查文件编码")

def read_template_with_encoding(filepath):
    """尝试多种编码读取模板文件"""
    with open(filepath, 'rb') as f:
        raw = f.read()
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb18030', 'gb2312']
    for enc in encodings:
        try:
            return raw.decode(enc)
        except Exception:
            continue
    raise ValueError(f"无法使用常见编码读取模板 {filepath}")

def generate_special_value(csv_col, row):
    """
    根据规则生成 CUSTOM、GPA、GPB 的值
    """
    dpu = str(row.get("DPU", "")).strip()
    sheet = str(row.get("SHEET", "")).strip()
    if not dpu or not sheet:
        return ""
    if csv_col == "CUSTOM":
        return f"A{dpu.zfill(3)}Z{sheet}"
    elif csv_col == "GPA":
        return f"G{dpu.zfill(2)}P{sheet}O1"
    elif csv_col == "GPB":
        return f"G{dpu.zfill(2)}P{sheet}O2"
    else:
        return ""

def process_csv_file(csv_path):
    """处理单个 CSV 文件"""
    print(f"\n处理文件: {csv_path}")
    try:
        data_df = read_csv_with_encoding(csv_path)
    except Exception as e:
        print(f"  读取失败: {e}")
        return

    # 检查必要的关键列是否存在
    for col in KEY_COLS:
        if col not in data_df.columns:
            print(f"  数据文件缺少必要列: {col}，跳过此文件")
            return

    # 逐行处理
    for idx, row in data_df.iterrows():
        # 获取关键字段
        domain = row.get("域名", "").strip()
        station = row.get("DPU", "").strip()
        sheet = row.get("SHEET", "").strip()
        device_name = row.get("设备名称", "").strip()
        driver_level = row.get("驱动级", "").strip()

        # 校验关键信息
        if not domain or not station or not sheet or not device_name:
            print(f"  第 {idx+2} 行缺少必要信息（域名/DPU/SHEET/设备名称），跳过")
            continue

        # 确定模板文件名
        template_file = determine_template(driver_level, row)
        if template_file is None:
            print(f"  第 {idx+2} 行驱动级 {driver_level} 无法匹配模板，跳过")
            continue

        # 读取模板内容
        template_path = os.path.join(TEMPLATE_DIR, template_file)
        if not os.path.isfile(template_path):
            print(f"  模板文件不存在: {template_path}")
            continue

        try:
            content = read_template_with_encoding(template_path)
        except Exception as e:
            print(f"  读取模板文件失败 {template_path}: {e}")
            continue

        # 替换占位符
        for csv_col, placeholder in MAPPING.items():
            if csv_col in ("CUSTOM", "GPA", "GPB"):
                value = generate_special_value(csv_col, row)
            else:
                value = row.get(csv_col, "")
                if pd.isna(value):
                    value = ""

                # 驱动级6：仅对“远方”和“故障”补零
                if driver_level == "6" and csv_col in ["远方", "故障"]:
                    if value == "" or value.upper() in ["#N/A", "#/A"]:
                        value = "0"

                # 驱动级7和11：对所有测点（启动、停止、已启、已停、故障、远方）补零
                if driver_level in ["7", "11"] and csv_col in POINT_COLS:
                    if value == "" or value.upper() in ["#N/A", "#/A"]:
                        value = "0"

            content = content.replace(placeholder, str(value))

        # 构造输出路径
        dir_path, filename = build_output_path(domain, station, sheet, device_name)
        os.makedirs(dir_path, exist_ok=True)

        output_path = os.path.join(dir_path, filename)
        with open(output_path, 'w', encoding='gb2312', newline='\n') as f:
            f.write(content)

        print(f"  已生成: {output_path}")

# ---------- 主流程 ----------
def main():
    if not os.path.isdir(INPUT_DIR):
        print(f"输入目录不存在: {INPUT_DIR}")
        sys.exit(1)

    csv_files = glob.glob(os.path.join(INPUT_DIR, "*.csv"))
    if not csv_files:
        print(f"在 {INPUT_DIR} 中未找到任何 .csv 文件")
        sys.exit(1)

    print(f"找到 {len(csv_files)} 个 CSV 文件")
    for csv_file in csv_files:
        process_csv_file(csv_file)

    print("\n全部处理完成")

if __name__ == "__main__":
    main()