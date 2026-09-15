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
        return os.path.join(sys._MEIPASS, "cb")
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "cb")

def get_default_output_dir():
    """默认输出目录：开发环境为脚本目录，打包后为exe所在目录"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# ---------- 全局变量 ----------
TEMPLATE_DIR = ""
OUTPUT_ROOT = ""

# ---------- 业务逻辑 ----------
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
unmatched_template_devices = []

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
        elif has_start and has_started and has_fault:
            return "MOTORII _1DO_NOT_ERR_1DI.cbp"
        elif has_start and has_started and not has_fault:
            return "MOTORII _1DO_NOT_1DI.cbp"
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
        elif not has_started and has_remote and has_start:
            # 新增：只有已启和远方（无启动）
            return "SCSOV_1DO_NOT.cbp"
        else:
            return None

    elif dl == "11":
        return "MOVSPII_NOT_ERR.cbp"
    else:
        return None

def build_output_path(output_root, domain, station, sheet, device_name):
    station_padded = str(station).zfill(3)
    dir_path = os.path.join(output_root, str(domain), f"drop{station_padded}")
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
    global missing_start_stop_devices, unmatched_template_devices
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
            unmatched_template_devices.append({
                "station": station,
                "sheet": sheet,
                "device_name": device_name,
                "driver_level": driver_level,
                "domain": domain,
            })
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

        dir_path, filename = build_output_path(OUTPUT_ROOT, domain, station, sheet, device_name)
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

    def __init__(self, input_dir, output_dir):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir

    def log(self, msg):
        self.log_signal.emit(msg)

    def run(self):
        try:
            global TEMPLATE_DIR, OUTPUT_ROOT, missing_start_stop_devices, unmatched_template_devices
            missing_start_stop_devices = []
            unmatched_template_devices = []

            TEMPLATE_DIR = get_template_dir()
            if not os.path.isdir(TEMPLATE_DIR):
                self.log(f"错误：模板目录 'cb' 不存在于 {TEMPLATE_DIR}")
                self.finished_signal.emit()
                return

            OUTPUT_ROOT = self.output_dir
            os.makedirs(OUTPUT_ROOT, exist_ok=True)
            self.log(f"输出根目录: {OUTPUT_ROOT}")

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

            if unmatched_template_devices:
                self.log("\n【驱动级无法匹配模板的设备列表（按站号）】")
                grouped = {}
                for item in unmatched_template_devices:
                    grouped.setdefault(item["station"], []).append(item)
                for station in sorted(grouped.keys(), key=lambda x: (len(x), x)):
                    self.log(f"站号 {station}:")
                    for item in grouped[station]:
                        self.log(
                            f"  域名:{item['domain']}, SHEET:{item['sheet']}, "
                            f"设备:{item['device_name']}, 驱动级:{item['driver_level']}"
                        )
            else:
                self.log("\n所有记录均成功匹配到模板。")

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
        self.setGeometry(100, 100, 850, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # ---------- 输入目录行 ----------
        input_layout = QHBoxLayout()
        self.input_label = QLabel("输入目录:")
        self.input_path_label = QLabel("未选择")
        self.input_path_label.setStyleSheet("border: 1px solid gray; padding: 3px;")
        self.choose_input_btn = QPushButton("选择目录")
        self.choose_input_btn.clicked.connect(self.choose_input_dir)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_path_label, 1)
        input_layout.addWidget(self.choose_input_btn)
        layout.addLayout(input_layout)

        # ---------- 输出目录行 ----------
        output_layout = QHBoxLayout()
        self.output_label = QLabel("输出目录:")
        self.output_path_label = QLabel(get_default_output_dir())
        self.output_path_label.setStyleSheet("border: 1px solid gray; padding: 3px;")
        self.choose_output_btn = QPushButton("选择目录")
        self.choose_output_btn.clicked.connect(self.choose_output_dir)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_path_label, 1)
        output_layout.addWidget(self.choose_output_btn)
        layout.addLayout(output_layout)

        # ---------- 日志文本框 ----------
        layout.addWidget(QLabel("处理日志:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # ---------- 底部按钮 ----------
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
        self.output_dir = get_default_output_dir()
        self.worker = None

    def choose_input_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择包含CSV文件的目录")
        if dir_path:
            self.input_dir = dir_path
            self.input_path_label.setText(dir_path)
            self.process_btn.setEnabled(True)

    def choose_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir = dir_path
            self.output_path_label.setText(dir_path)

    def start_process(self):
        if not self.input_dir:
            QMessageBox.warning(self, "提示", "请先选择输入目录")
            return
        if not self.output_dir:
            QMessageBox.warning(self, "提示", "请先选择输出目录")
            return

        self.process_btn.setEnabled(False)
        self.log_text.append("开始处理...")
        self.log_text.append(f"输入目录: {self.input_dir}")
        self.log_text.append(f"输出目录: {self.output_dir}")
        self.worker = WorkerThread(self.input_dir, self.output_dir)
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