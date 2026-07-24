#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
import pandas as pd
from io import StringIO
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit, QFileDialog,
                             QLabel, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal

# ---------- 辅助函数：获取模板目录 ----------
def get_template_dir():
    """返回模板目录路径，支持开发环境和打包环境"""
    if getattr(sys, 'frozen', False):
        # 打包后，模板文件被解压到 sys._MEIPASS
        return os.path.join(sys._MEIPASS, "cb")
    else:
        # 开发环境，模板文件夹位于脚本同级
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "cb")

# ---------- 全局变量 ----------
TEMPLATE_DIR = ""   # 将在 WorkerThread 中赋值

# ---------- 业务逻辑（与原驱动级创建V2_gui_ok.py一致） ----------
POINT_COLS = ["启动", "停止", "已启", "已停", "故障", "远方"]
KEY_COLS = ["域名", "DPU", "SHEET", "设备名称", "驱动级"]

MAPPING = {
    "DM": "DM",
    "DPU": "DPUNUM",
    "启动": "INPUT1",
    "停止": "INPUT2",
    "已启": "OUTPUT1",
    "已停": "OUTPUT2",
    "SHEET": "SHEETNUM",
    "设备名称": "equipment",
    "CUSTOM": "CUSTOM",
    "GPA": "GPA",
    "GPB": "GPB",
    "故障": "ERR",
    "远方": "NOSPOT",
    "就地": "SPOT"
}

missing_start_stop_devices = []

def is_valid(value):
    if pd.isna(value):
        return False
    if isinstance(value, str):
        v = value.strip()
        if v == "" or v.upper() in ["#N/A", "#/A"]:
            return False
    return True

def get_point_status(row):
    status = {}
    for col in POINT_COLS:
        status[col] = is_valid(row.get(col))
    return status

def determine_template(driver_level, row):
    dl = str(driver_level).strip()
    s = get_point_status(row)
    has_start  = s["启动"]
    has_stop   = s["停止"]
    has_started = s["已启"]
    has_stopped = s["已停"]
    has_fault  = s["故障"]
    has_remote = s["远方"]

    if dl == "5":
        if has_start and has_stop and has_started:
            if not has_fault and not has_remote:
                return "MOV.cbp"
            elif has_fault and not has_remote:
                return "MOV_ERR.cbp"
            elif not has_fault and has_remote:
                return "MOV_NOT.cbp"
            elif has_fault and has_remote:
                return "MOV_NOT_ERR.cbp"
        return None

    elif dl == "6":
        if has_start and has_stop and has_started and has_stopped:
            return "MOTORII_NOT_ERR.cbp"
        elif has_start and has_stop and has_started:
            return "MOTORII_NOT_ERR_1DI.cbp"
        elif has_start and has_started:
            return "MOTORII _1DO_NOT_ERR_1DI.cbp"
        else:
            return None

    elif dl == "7":
        return "BREAKERII_NOT_ERR.cbp"

    elif dl == "9":
        if has_start and has_started and has_remote:
            return "SCSOV_NOT.cbp"
        elif has_start and has_started and not has_remote:
            return "SCSOV.cbp"
        elif has_start and not has_started and not has_remote:
            return "SCSOV_1DO.cbp"
        else:
            return None

    elif dl == "11":
        return "MOVSPII_NOT_ERR.cbp"
    else:
        return None

def build_output_path(domain, station, sheet, device_name):
    station_padded = str(station).zfill(3)
    dir_path = os.path.join(str(domain), f"drop{station_padded}")
    filename = f"SH{sheet}_{device_name}.cbp"
    return dir_path, filename

def read_csv_with_encoding(filepath):
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

def process_single_csv(csv_path, log_callback=None):
    """处理单个CSV文件，log_callback用于输出日志"""
    global missing_start_stop_devices
    if log_callback:
        log_callback(f"\n处理文件: {csv_path}")

    try:
        data_df = read_csv_with_encoding(csv_path)
    except Exception as e:
        if log_callback:
            log_callback(f"  读取失败: {e}")
        return

    for col in KEY_COLS:
        if col not in data_df.columns:
            if log_callback:
                log_callback(f"  数据文件缺少必要列: {col}，跳过此文件")
            return

    for idx, row in data_df.iterrows():
        domain = row.get("域名", "").strip()
        station = row.get("DPU", "").strip()
        sheet = row.get("SHEET", "").strip()
        device_name = row.get("设备名称", "").strip()
        driver_level = row.get("驱动级", "").strip()

        if not domain or not station or not sheet or not device_name:
            if log_callback:
                log_callback(f"  第 {idx+2} 行缺少必要信息（域名/DPU/SHEET/设备名称），跳过")
            continue

        # 汇总驱动级5缺失启动/停止
        if driver_level == "5":
            start_val = row.get("启动", "")
            stop_val = row.get("停止", "")
            if not is_valid(start_val) or not is_valid(stop_val):
                missing_start_stop_devices.append(
                    f"域名:{domain}, DPU:{station}, SHEET:{sheet}, 设备名称:{device_name}"
                )

        template_file = determine_template(driver_level, row)
        if template_file is None:
            if log_callback:
                log_callback(f"  第 {idx+2} 行驱动级 {driver_level} 无法匹配模板，跳过")
            continue

        template_path = os.path.join(TEMPLATE_DIR, template_file)
        if not os.path.isfile(template_path):
            if log_callback:
                log_callback(f"  模板文件不存在: {template_path}")
            continue

        try:
            content = read_template_with_encoding(template_path)
        except Exception as e:
            if log_callback:
                log_callback(f"  读取模板文件失败 {template_path}: {e}")
            continue

        for csv_col, placeholder in MAPPING.items():
            if csv_col in ("CUSTOM", "GPA", "GPB"):
                value = generate_special_value(csv_col, row)
            else:
                value = row.get(csv_col, "")
                if pd.isna(value):
                    value = ""

                if driver_level == "5" and csv_col == "已停":
                    if value == "" or value.upper() in ["#N/A", "#/A"]:
                        value = "0"
                if driver_level == "6" and csv_col in ["远方", "故障"]:
                    if value == "" or value.upper() in ["#N/A", "#/A"]:
                        value = "0"
                if driver_level in ["7", "11"] and csv_col in POINT_COLS:
                    if value == "" or value.upper() in ["#N/A", "#/A"]:
                        value = "0"
                if driver_level == "9" and csv_col in POINT_COLS:
                    if value == "" or value.upper() in ["#N/A", "#/A"]:
                        value = "0"

            content = content.replace(placeholder, str(value))

        dir_path, filename = build_output_path(domain, station, sheet, device_name)
        os.makedirs(dir_path, exist_ok=True)
        output_path = os.path.join(dir_path, filename)
        with open(output_path, 'w', encoding='gb2312', newline='\n') as f:
            f.write(content)

        if log_callback:
            log_callback(f"  已生成: {output_path}")

# ---------- PyQt5 GUI 部分 ----------
class WorkerThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, input_dir):
        super().__init__()
        self.input_dir = input_dir

    def log(self, msg):
        self.log_signal.emit(msg)

    def run(self):
        try:
            global TEMPLATE_DIR, missing_start_stop_devices
            missing_start_stop_devices = []  # 重置

            # 获取模板目录（支持打包环境）
            TEMPLATE_DIR = get_template_dir()
            if not os.path.isdir(TEMPLATE_DIR):
                self.log(f"错误：模板目录 'cb' 不存在于 {TEMPLATE_DIR}")
                self.finished_signal.emit()
                return

            # 扫描CSV文件
            csv_files = glob.glob(os.path.join(self.input_dir, "*.csv"))
            if not csv_files:
                self.log(f"在 {self.input_dir} 中未找到任何 .csv 文件")
                self.finished_signal.emit()
                return

            self.log(f"找到 {len(csv_files)} 个 CSV 文件")
            for csv_file in csv_files:
                process_single_csv(csv_file, log_callback=self.log)

            if missing_start_stop_devices:
                self.log("\n【驱动级5中启动或停止缺失的设备列表】")
                for info in missing_start_stop_devices:
                    self.log(info)

            self.log("\n全部处理完成")
        except Exception as e:
            import traceback
            self.log(f"\n*** 发生异常: {e}")
            self.log(traceback.format_exc())
        finally:
            self.finished_signal.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CBP 文件生成工具")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 选择目录行
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("输入目录:")
        self.dir_path_label = QLabel("未选择")
        self.dir_path_label.setStyleSheet("border: 1px solid gray; padding: 3px;")
        self.choose_dir_btn = QPushButton("选择目录")
        self.choose_dir_btn.clicked.connect(self.choose_input_dir)
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.dir_path_label, 1)
        dir_layout.addWidget(self.choose_dir_btn)
        layout.addLayout(dir_layout)

        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(QLabel("处理日志:"))
        layout.addWidget(self.log_text)

        # 底部按钮
        btn_layout = QHBoxLayout()
        self.process_btn = QPushButton("开始处理")
        self.process_btn.clicked.connect(self.start_process)
        self.process_btn.setEnabled(False)
        self.clear_btn = QPushButton("清空日志")
        self.clear_btn.clicked.connect(self.log_text.clear)
        btn_layout.addStretch()
        btn_layout.addWidget(self.process_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)

        self.input_dir = None
        self.worker = None

    def choose_input_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择包含CSV文件的目录")
        if dir_path:
            self.input_dir = dir_path
            self.dir_path_label.setText(dir_path)
            self.process_btn.setEnabled(True)

    def start_process(self):
        if not self.input_dir:
            QMessageBox.warning(self, "提示", "请先选择输入目录")
            return

        self.process_btn.setEnabled(False)
        self.log_text.append("开始处理...")
        self.worker = WorkerThread(self.input_dir)
        self.worker.log_signal.connect(self.append_log)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def append_log(self, msg):
        self.log_text.append(msg)

    def on_finished(self):
        self.process_btn.setEnabled(True)
        self.log_text.append("\n处理结束。")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()