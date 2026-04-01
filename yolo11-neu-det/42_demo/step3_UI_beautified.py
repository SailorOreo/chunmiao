#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import copy                      # 用于图像复制
import os                        # 用于系统路径查找
import shutil                    # 用于复制
from distutils.command.config import config
from PySide6.QtGui import *      # GUI组件
from PySide6.QtCore import *     # 字体、边距等系统变量
from PySide6.QtWidgets import *  # 窗口等小组件
import threading                 # 多线程
import sys                       # 系统库
import cv2                       # opencv图像处理
import torch                     # 深度学习框架
import os.path as osp            # 路径查找
import time                      # 时间计算
from ultralytics import YOLO     # yolo核心算法
from ultralytics.utils.torch_utils import select_device
from collections import defaultdict, UserDict
import numpy as np

# 常用的字符串常量
WINDOW_TITLE = "Defect detection system"            # 系统上方标题
WELCOME_SENTENCE = "欢迎使用基于图像识别的工业缺陷检测系统"      # 欢迎的句子
ICON_IMAGE = "images/UI/lufei.png"                 # 系统logo界面
IMAGE_LEFT_INIT = "images/UI/up.jpeg"              # 图片检测界面初始化左侧图像
IMAGE_RIGHT_INIT = "images/UI/right.jpeg"          # 图片检测界面初始化右侧图像
ZHU_IMAGE_PATH = "images/UI/zhu.jpg"
USERNAME = "1"
PASSWORD = "1"
LOGIN_TITLE = "欢迎使用基于图像识别的工业缺陷检测系统\n "

# http://192.168.247.7:8090/stream.mjpg


class CardFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.setFrameShape(QFrame.StyledPanel)


class MainWindow(QTabWidget):
    def __init__(self):
        # 初始化界面
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)       # 系统界面标题
        self.resize(1200, 800)                  # 系统初始化大小
        self.setWindowIcon(QIcon(ICON_IMAGE))   # 系统logo图像
        self.output_size = 480                  # 上传的图像和视频在系统界面上显示的大小
        self.img2predict = ""                   # 要进行预测的图像路径
        # 用来进行设置的参数
        self.init_vid_id = '1'                  # 网络摄像头修改 包括ip或者是ip地址的修改
        self.vid_source = int(self.init_vid_id) # 需要设置为对应的整数，加载的才是usb的摄像头
        self.conf_thres = 0.35   # 置信度的阈值
        self.iou_thres = 0.45    # NMS操作的时候 IOU过滤的阈值
        self.save_txt = False
        self.save_conf = False
        self.save_crop = False
        self.vid_gap = 15        # 摄像头视频帧保存间隔。
        self.is_open_track = ""  # 三种选择，如果是空表示不开启追踪，否则有两种追踪器可以进行选择

        self.cap = cv2.VideoCapture(self.vid_source)
        self.stopEvent = threading.Event()
        self.webcam = True
        self.stopEvent.clear()
        self.model_path = "runs/yolo11n_cbam/train8/weights/best.pt"
        self.model = self.model_load(weights=self.model_path)

        self.apply_global_style()
        self.initUI()            # 初始化图形化界面
        self.reset_vid()         # 重新设置视频参数，重新初始化是为了防止视频加载出错

    # 模型初始化
    @torch.no_grad()
    def model_load(self, weights=""):
        """
        模型加载
        """
        model_loaded = YOLO(weights)
        return model_loaded

    def apply_global_style(self):
        self.setDocumentMode(True)
        self.setMovable(False)
        self.setElideMode(Qt.ElideRight)
        self.setStyleSheet("""
            QWidget {
                background: #f5f7fb;
                color: #1f2937;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                font-size: 14px;
            }
            QTabWidget::pane {
                border: 1px solid #dbe2ea;
                background: #ffffff;
                border-radius: 14px;
                top: -1px;
            }
            QTabBar::tab {
                background: #e9eef5;
                color: #4b5563;
                border: 1px solid #dbe2ea;
                padding: 10px 22px;
                margin-right: 6px;
                min-width: 110px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #1677ff;
                border-bottom: 1px solid #ffffff;
            }
            QTabBar::tab:hover {
                color: #1677ff;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #1677ff, stop:1 #4096ff);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 18px;
                min-height: 18px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #0f67e6, stop:1 #2f86f6);
            }
            QPushButton:pressed {
                padding-top: 11px;
                padding-bottom: 9px;
            }
            QPushButton:disabled {
                background: #b9c6d8;
                color: #eef3f8;
            }
            QLabel[role="title"] {
                font-size: 24px;
                font-weight: 700;
                color: #0f172a;
                background: transparent;
            }
            QLabel[role="subtitle"] {
                font-size: 15px;
                color: #64748b;
                background: transparent;
            }
            QLabel[role="section"] {
                font-size: 18px;
                font-weight: 700;
                color: #0f172a;
                background: transparent;
            }
            QLabel[role="status"] {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 14px;
                color: #334155;
            }
            QLineEdit, QComboBox {
                background: #ffffff;
                border: 1px solid #d6dee8;
                border-radius: 10px;
                padding: 8px 12px;
                min-height: 20px;
                selection-background-color: #1677ff;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #1677ff;
            }
            QComboBox::drop-down {
                border: none;
                width: 28px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #d6dee8;
                background: white;
                selection-background-color: #e8f1ff;
                selection-color: #1677ff;
            }
            QRadioButton {
                spacing: 8px;
                color: #334155;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #b8c4d3;
                border-radius: 9px;
                background: white;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #1677ff;
                border-radius: 9px;
                background: #1677ff;
            }
            QFrame#cardFrame {
                background: #ffffff;
                border: 1px solid #e6edf5;
                border-radius: 16px;
            }
            QMessageBox {
                background: #ffffff;
            }
        """)

    def make_title_label(self, text):
        label = QLabel(text)
        label.setProperty("role", "title")
        label.setAlignment(Qt.AlignCenter)
        return label

    def make_section_label(self, text):
        label = QLabel(text)
        label.setProperty("role", "section")
        return label

    def make_status_label(self, text):
        label = QLabel(text)
        label.setProperty("role", "status")
        label.setWordWrap(True)
        return label

    def wrap_image_label(self, pixmap_path):
        frame = CardFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(0)
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        label.setMinimumHeight(360)
        label.setStyleSheet("QLabel { background: #f8fafc; border-radius: 12px; }")
        label.setPixmap(QPixmap(pixmap_path))
        layout.addWidget(label)
        return frame, label

    def initUI(self):
        """
        图形化界面初始化
        """
        font_title = QFont('Microsoft YaHei', 15)
        font_main = QFont('Microsoft YaHei', 11)

        # ********************* 图片识别界面 *****************************
        img_detection_widget = QWidget()
        img_detection_layout = QVBoxLayout(img_detection_widget)
        img_detection_layout.setContentsMargins(24, 24, 24, 24)
        img_detection_layout.setSpacing(18)

        img_detection_title = self.make_title_label("图片检测功能")
        img_detection_desc = QLabel("上传单张图片并执行工业缺陷检测，左侧显示原图，右侧显示识别结果。")
        img_detection_desc.setProperty("role", "subtitle")
        img_detection_desc.setAlignment(Qt.AlignCenter)

        mid_img_widget = QWidget()
        mid_img_layout = QHBoxLayout(mid_img_widget)
        mid_img_layout.setContentsMargins(0, 0, 0, 0)
        mid_img_layout.setSpacing(18)

        left_frame, self.left_img = self.wrap_image_label(IMAGE_LEFT_INIT)
        right_frame, self.right_img = self.wrap_image_label(IMAGE_RIGHT_INIT)
        mid_img_layout.addWidget(left_frame)
        mid_img_layout.addWidget(right_frame)

        self.img_num_label = self.make_status_label("当前检测结果：待检测")
        self.img_num_label.setFont(font_main)

        button_row = QWidget()
        button_row_layout = QHBoxLayout(button_row)
        button_row_layout.setContentsMargins(0, 0, 0, 0)
        button_row_layout.setSpacing(12)
        up_img_button = QPushButton("上传图片")
        det_img_button = QPushButton("开始检测")
        up_img_button.clicked.connect(self.upload_img)
        det_img_button.clicked.connect(self.detect_img)
        up_img_button.setFont(font_main)
        det_img_button.setFont(font_main)
        button_row_layout.addStretch()
        button_row_layout.addWidget(up_img_button)
        button_row_layout.addWidget(det_img_button)
        button_row_layout.addStretch()

        img_detection_layout.addWidget(img_detection_title)
        img_detection_layout.addWidget(img_detection_desc)
        img_detection_layout.addWidget(mid_img_widget)
        img_detection_layout.addWidget(self.img_num_label)
        img_detection_layout.addWidget(button_row)

        # ********************* 视频识别界面 *****************************
        vid_detection_widget = QWidget()
        vid_detection_layout = QVBoxLayout(vid_detection_widget)
        vid_detection_layout.setContentsMargins(24, 24, 24, 24)
        vid_detection_layout.setSpacing(18)

        vid_title = self.make_title_label("视频检测功能")
        vid_desc = QLabel("支持摄像头实时监测与视频文件检测，界面下方同步展示检测结果统计。")
        vid_desc.setProperty("role", "subtitle")
        vid_desc.setAlignment(Qt.AlignCenter)

        vid_frame, self.vid_img = self.wrap_image_label(IMAGE_LEFT_INIT)
        self.webcam_detection_btn = QPushButton("摄像头实时监测")
        self.mp4_detection_btn = QPushButton("视频文件检测")
        self.vid_stop_btn = QPushButton("停止检测")
        self.webcam_detection_btn.setFont(font_main)
        self.mp4_detection_btn.setFont(font_main)
        self.vid_stop_btn.setFont(font_main)
        self.webcam_detection_btn.clicked.connect(self.open_cam)
        self.mp4_detection_btn.clicked.connect(self.open_mp4)
        self.vid_stop_btn.clicked.connect(self.close_vid)

        vid_button_row = QWidget()
        vid_button_row_layout = QHBoxLayout(vid_button_row)
        vid_button_row_layout.setContentsMargins(0, 0, 0, 0)
        vid_button_row_layout.setSpacing(12)
        vid_button_row_layout.addWidget(self.webcam_detection_btn)
        vid_button_row_layout.addWidget(self.mp4_detection_btn)
        vid_button_row_layout.addWidget(self.vid_stop_btn)

        self.vid_num_label = self.make_status_label("当前检测结果：等待检测")
        self.vid_num_label.setFont(font_main)

        vid_detection_layout.addWidget(vid_title)
        vid_detection_layout.addWidget(vid_desc)
        vid_detection_layout.addWidget(vid_frame)
        vid_detection_layout.addWidget(self.vid_num_label)
        vid_detection_layout.addWidget(vid_button_row)

        # ********************* 模型切换界面 *****************************
        about_widget = QWidget()
        about_layout = QVBoxLayout(about_widget)
        about_layout.setContentsMargins(24, 24, 24, 24)
        about_layout.setSpacing(18)

        hero_card = CardFrame()
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(24, 24, 24, 24)
        hero_layout.setSpacing(14)

        about_title = self.make_title_label(WELCOME_SENTENCE)
        about_img = QLabel()
        about_img.setAlignment(Qt.AlignCenter)
        about_img.setPixmap(QPixmap(ZHU_IMAGE_PATH))
        self.model_label = self.make_status_label("当前模型：{}".format(self.model_path))
        self.model_label.setFont(font_main)

        change_model_button = QPushButton("切换模型")
        change_model_button.setFont(font_main)
        record_button = QPushButton("查看历史记录")
        record_button.setFont(font_main)
        record_button.clicked.connect(self.check_record)
        change_model_button.clicked.connect(self.change_model)

        about_button_row = QWidget()
        about_button_layout = QHBoxLayout(about_button_row)
        about_button_layout.setContentsMargins(0, 0, 0, 0)
        about_button_layout.setSpacing(12)
        about_button_layout.addStretch()
        about_button_layout.addWidget(change_model_button)
        about_button_layout.addWidget(record_button)
        about_button_layout.addStretch()

        label_super = QLabel()
        label_super.setText("<a </a>")
        label_super.setFont(QFont('Microsoft YaHei', 11))
        label_super.setOpenExternalLinks(True)
        label_super.setAlignment(Qt.AlignRight)
        label_super.setStyleSheet("color: #94a3b8; background: transparent;")

        hero_layout.addWidget(about_title)
        hero_layout.addWidget(about_img)
        hero_layout.addWidget(self.model_label)
        hero_layout.addWidget(about_button_row)
        hero_layout.addWidget(label_super)
        about_layout.addWidget(hero_card)

        self.left_img.setAlignment(Qt.AlignCenter)

        # ********************* 配置切换界面 ****************************
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        config_layout.setContentsMargins(24, 24, 24, 24)
        config_layout.setSpacing(18)

        config_vid_title = self.make_title_label("配置信息修改")
        config_icon_label = QLabel()
        config_icon_label.setPixmap(QPixmap("images/UI/config.png"))
        config_icon_label.setAlignment(Qt.AlignCenter)

        config_card = CardFrame()
        config_card_layout = QVBoxLayout(config_card)
        config_card_layout.setContentsMargins(24, 24, 24, 24)
        config_card_layout.setSpacing(18)

        config_grid_widget = QWidget()
        config_grid_layout = QGridLayout(config_grid_widget)
        config_grid_layout.setHorizontalSpacing(16)
        config_grid_layout.setVerticalSpacing(16)
        config_grid_layout.setContentsMargins(0, 0, 0, 0)

        row = 0
        config_output_size_label = QLabel("系统图像显示大小")
        self.config_output_size_value = QLineEdit("")
        self.config_output_size_value.setText(str(self.output_size))
        config_grid_layout.addWidget(config_output_size_label, row, 0)
        config_grid_layout.addWidget(self.config_output_size_value, row, 1)
        row += 1

        config_vid_source_label = QLabel("摄像头源地址")
        self.config_vid_source_value = QLineEdit("")
        self.config_vid_source_value.setText(str(self.vid_source))
        config_grid_layout.addWidget(config_vid_source_label, row, 0)
        config_grid_layout.addWidget(self.config_vid_source_value, row, 1)
        row += 1

        config_vid_gap_label = QLabel("视频帧保存间隔")
        self.config_vid_gap_value = QLineEdit("")
        self.config_vid_gap_value.setText(str(self.vid_gap))
        config_grid_layout.addWidget(config_vid_gap_label, row, 0)
        config_grid_layout.addWidget(self.config_vid_gap_value, row, 1)
        row += 1

        config_conf_thres_label = QLabel("检测模型置信度阈值")
        self.config_conf_thres_value = QLineEdit("")
        self.config_conf_thres_value.setText(str(self.conf_thres))
        config_grid_layout.addWidget(config_conf_thres_label, row, 0)
        config_grid_layout.addWidget(self.config_conf_thres_value, row, 1)
        row += 1

        config_iou_thres_label = QLabel("检测模型IOU阈值")
        self.config_iou_thres_value = QLineEdit("")
        self.config_iou_thres_value.setText(str(self.iou_thres))
        config_grid_layout.addWidget(config_iou_thres_label, row, 0)
        config_grid_layout.addWidget(self.config_iou_thres_value, row, 1)
        row += 1

        config_save_txt_label = QLabel("推理时是否保存txt文件")
        self.config_save_txt_value = QRadioButton("True")
        self.config_save_txt_value.setChecked(False)
        self.config_save_txt_value.setAutoExclusive(False)
        config_grid_layout.addWidget(config_save_txt_label, row, 0)
        config_grid_layout.addWidget(self.config_save_txt_value, row, 1)
        row += 1

        config_save_conf_label = QLabel("推理时是否保存置信度")
        self.config_save_conf_value = QRadioButton("True")
        self.config_save_conf_value.setChecked(False)
        self.config_save_conf_value.setAutoExclusive(False)
        config_grid_layout.addWidget(config_save_conf_label, row, 0)
        config_grid_layout.addWidget(self.config_save_conf_value, row, 1)
        row += 1

        config_save_crop_label = QLabel("推理时是否保存切片文件")
        self.config_save_crop_value = QRadioButton("True")
        self.config_save_crop_value.setChecked(False)
        self.config_save_crop_value.setAutoExclusive(False)
        config_grid_layout.addWidget(config_save_crop_label, row, 0)
        config_grid_layout.addWidget(self.config_save_crop_value, row, 1)
        row += 1

        config_track_label = QLabel("追踪配置")
        self.config_track_value = QComboBox(self)
        self.config_track_value.addItems(['不开启追踪', "bytetrack.yaml", "botsort.yaml"])
        config_grid_layout.addWidget(config_track_label, row, 0)
        config_grid_layout.addWidget(self.config_track_value, row, 1)

        save_config_button = QPushButton("保存配置信息")
        save_config_button.setFont(font_main)
        save_config_button.clicked.connect(self.save_config_change)

        config_card_layout.addWidget(config_icon_label)
        config_card_layout.addWidget(config_grid_widget)
        config_card_layout.addWidget(save_config_button)

        config_layout.addWidget(config_vid_title)
        config_layout.addWidget(config_card)

        self.addTab(about_widget, '主页')
        self.addTab(img_detection_widget, '图片检测')
        self.addTab(vid_detection_widget, '视频检测')
        self.addTab(config_widget, '配置信息')
        self.setTabIcon(0, QIcon(ICON_IMAGE))
        self.setTabIcon(1, QIcon(ICON_IMAGE))
        self.setTabIcon(2, QIcon(ICON_IMAGE))
        self.setTabIcon(3, QIcon(ICON_IMAGE))

    def upload_img(self):
        """上传图像，图像要尽可能保证是中文格式"""
        fileName, fileType = QFileDialog.getOpenFileName(self, 'Choose file', '', '*.jpg *.png *.tif *.jpeg')
        if fileName:
            suffix = fileName.split(".")[-1]
            save_path = osp.join("images/tmp", "tmp_upload." + suffix)
            shutil.copy(fileName, save_path)
            im0 = cv2.imread(save_path)
            resize_scale = self.output_size / im0.shape[0]
            im0 = cv2.resize(im0, (0, 0), fx=resize_scale, fy=resize_scale)
            cv2.imwrite("images/tmp/upload_show_result.jpg", im0)
            self.img2predict = save_path
            self.left_img.setPixmap(QPixmap("images/tmp/upload_show_result.jpg"))
            self.right_img.setPixmap(QPixmap(IMAGE_RIGHT_INIT))
            self.img_num_label.setText("当前检测结果：待检测")

    def change_model(self):
        """切换模型，重新对self.model进行赋值"""
        fileName, fileType = QFileDialog.getOpenFileName(self, 'Choose file', '', '*.pt')
        if fileName:
            self.model_path = fileName
            self.model = self.model_load(weights=self.model_path)
            QMessageBox.information(self, "成功", "模型切换成功！")
            self.model_label.setText("当前模型：{}".format(self.model_path))

    def detect_img(self):
        """检测单张的图像文件"""
        output_size = self.output_size
        print(self.save_txt)
        results = self.model(self.img2predict, conf=self.conf_thres, iou=self.iou_thres,
                             save_txt=self.save_txt, save_conf=self.save_conf, save_crop=self.save_crop)
        result = results[0]
        img_array = result.plot()
        im0 = img_array
        im_record = copy.deepcopy(im0)
        resize_scale = output_size / im0.shape[0]
        im0 = cv2.resize(im0, (0, 0), fx=resize_scale, fy=resize_scale)
        cv2.imwrite("images/tmp/single_result.jpg", im0)
        self.right_img.setPixmap(QPixmap("images/tmp/single_result.jpg"))
        time_re = str(time.strftime('result_%Y-%m-%d_%H-%M-%S_%A'))
        cv2.imwrite("record/img/{}.jpg".format(time_re), im_record)
        result_names = result.names
        result_nums = [0 for i in range(0, len(result_names))]
        cls_ids = list(result.boxes.cls.cpu().numpy())
        for cls_id in cls_ids:
            result_nums[int(cls_id)] = result_nums[int(cls_id)] + 1
        result_info = ""
        for idx_cls, cls_num in enumerate(result_nums):
            if cls_num > 0:
                result_info = result_info + "{}:{}\n".format(result_names[idx_cls], cls_num)
        self.img_num_label.setText("当前检测结果\n{}".format(result_info))
        QMessageBox.information(self, "检测成功", "日志已保存！")

    def open_cam(self):
        """打开摄像头上传"""
        self.webcam_detection_btn.setEnabled(False)
        self.mp4_detection_btn.setEnabled(False)
        self.vid_stop_btn.setEnabled(True)
        if str(self.vid_source).isdigit():
            self.vid_source = int(self.vid_source)
        self.webcam = True
        print(f"当前实时源：{self.vid_source}")
        self.cap = cv2.VideoCapture(self.vid_source)
        th = threading.Thread(target=self.detect_vid)
        th.start()

    def open_mp4(self):
        """打开mp4文件上传"""
        fileName, fileType = QFileDialog.getOpenFileName(self, 'Choose file', '', '*.mp4 *.avi')
        if fileName:
            self.webcam_detection_btn.setEnabled(False)
            self.mp4_detection_btn.setEnabled(False)
            self.vid_source = fileName
            self.webcam = False
            self.cap = cv2.VideoCapture(self.vid_source)
            th = threading.Thread(target=self.detect_vid)
            th.start()

    def detect_vid(self):
        """检测视频文件，这里的视频文件包含了mp4格式的视频文件和摄像头形式的视频文件"""
        vid_i = 0
        track_history = defaultdict(lambda: [])
        while self.cap.isOpened():
            success, frame = self.cap.read()
            if success:
                if self.config_track_value.currentText() == "不开启追踪":
                    results = self.model(frame, conf=self.conf_thres, iou=self.iou_thres,
                                         save_txt=self.save_txt, save_conf=self.save_conf, save_crop=self.save_crop)
                    result = results[0]
                    img_array = result.plot()
                    im0 = img_array
                    im_record = copy.deepcopy(im0)
                    resize_scale = self.output_size / im0.shape[0]
                    im0 = cv2.resize(im0, (0, 0), fx=resize_scale, fy=resize_scale)
                    cv2.imwrite("images/tmp/single_result_vid.jpg", im0)
                    self.vid_img.setPixmap(QPixmap("images/tmp/single_result_vid.jpg"))
                    time_re = str(time.strftime('result_%Y-%m-%d_%H-%M-%S_%A'))
                    if vid_i % self.vid_gap == 0:
                        cv2.imwrite("record/vid/{}.jpg".format(time_re), im_record)
                    result_names = result.names
                    result_nums = [0 for i in range(0, len(result_names))]
                    cls_ids = list(result.boxes.cls.cpu().numpy())
                    for cls_id in cls_ids:
                        result_nums[int(cls_id)] = result_nums[int(cls_id)] + 1
                    result_info = ""
                    for idx_cls, cls_num in enumerate(result_nums):
                        if cls_num > 0:
                            result_info = result_info + "{}:{}\n".format(result_names[idx_cls], cls_num)
                    self.vid_num_label.setText("当前检测结果：\n{}".format(result_info))
                    vid_i = vid_i + 1
                else:
                    results = self.model.track(frame, conf=self.conf_thres, iou=self.iou_thres,
                                               save_txt=self.save_txt, save_conf=self.save_conf,
                                               save_crop=self.save_crop,
                                               tracker=self.config_track_value.currentText(), persist=True)
                    result = results[0]
                    img_array = result.plot()
                    try:
                        boxes = results[0].boxes.xywh.cpu()
                        track_ids = results[0].boxes.id.int().cpu().tolist()
                        for box, track_id in zip(boxes, track_ids):
                            x, y, w, h = box
                            track = track_history[track_id]
                            track.append((float(x), float(y)))
                            if len(track) > 30:
                                track.pop(0)
                            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                            cv2.polylines(img_array, [points], isClosed=False, color=(0, 0, 230), thickness=5)
                    except:
                        print("not got targets")
                    im0 = img_array
                    im_record = copy.deepcopy(im0)
                    resize_scale = self.output_size / im0.shape[0]
                    im0 = cv2.resize(im0, (0, 0), fx=resize_scale, fy=resize_scale)
                    cv2.imwrite("images/tmp/single_result_vid.jpg", im0)
                    self.vid_img.setPixmap(QPixmap("images/tmp/single_result_vid.jpg"))
                    time_re = str(time.strftime('result_%Y-%m-%d_%H-%M-%S_%A'))
                    if vid_i % self.vid_gap == 0:
                        cv2.imwrite("record/vid/{}.jpg".format(time_re), im_record)
                    result_names = result.names
                    result_nums = [0 for i in range(0, len(result_names))]
                    cls_ids = list(result.boxes.cls.cpu().numpy())
                    for cls_id in cls_ids:
                        result_nums[int(cls_id)] = result_nums[int(cls_id)] + 1
                    result_info = ""
                    for idx_cls, cls_num in enumerate(result_nums):
                        if cls_num > 0:
                            result_info = result_info + "{}:{}\n".format(result_names[idx_cls], cls_num)
                    self.vid_num_label.setText("当前检测结果：\n{}".format(result_info))
                    vid_i = vid_i + 1
            if cv2.waitKey(1) & self.stopEvent.is_set() == True:
                self.stopEvent.clear()
                self.webcam_detection_btn.setEnabled(True)
                self.mp4_detection_btn.setEnabled(True)
                if self.cap is not None:
                    self.cap.release()
                    cv2.destroyAllWindows()
                self.reset_vid()
                break

    def reset_vid(self):
        """重置摄像头内容"""
        self.webcam_detection_btn.setEnabled(True)
        self.mp4_detection_btn.setEnabled(True)
        self.vid_img.setPixmap(QPixmap(IMAGE_LEFT_INIT))
        self.webcam = True
        self.vid_num_label.setText("当前检测结果：{}".format("等待检测"))

    def close_vid(self):
        """关闭摄像头"""
        self.stopEvent.set()
        self.reset_vid()

    def check_record(self):
        """打开历史记录文件夹"""
        os.startfile(osp.join(os.path.abspath(os.path.dirname(__file__)), "record"))

    def save_config_change(self):
        print("保存配置修改的结果")
        try:
            self.output_size = int(self.config_output_size_value.text())
            self.vid_source = str(self.config_vid_source_value.text())
            print(f"源地址:{self.vid_source}")
            self.vid_gap = int(self.config_vid_gap_value.text())
            self.conf_thres = float(self.config_conf_thres_value.text())
            self.iou_thres = float(self.config_iou_thres_value.text())
            self.save_txt = self.config_save_txt_value.isChecked()
            self.save_conf = self.config_save_conf_value.isChecked()
            self.save_crop = self.config_save_crop_value.isChecked()
            QMessageBox.information(self, "配置文件保存成功", "配置文件保存成功")
        except:
            QMessageBox.warning(self, "配置文件保存失败", "配置文件保存失败")

    def closeEvent(self, event):
        """用户退出事件"""
        reply = QMessageBox.question(self,
                                     'quit',
                                     "Are you sure?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if self.cap is not None:
                    self.cap.release()
                    print("摄像头已释放")
            except:
                pass
            self.close()
            event.accept()
        else:
            event.ignore()


class LoginWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        font_title = QFont('Microsoft YaHei', 13)
        self.setWindowTitle("识别系统登录界面")
        self.resize(860, 620)
        self.setWindowIcon(QIcon(ICON_IMAGE))
        self.setStyleSheet("""
            QWidget {
                background: #f3f6fb;
                color: #1f2937;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
            }
            QFrame#loginCard {
                background: #ffffff;
                border: 1px solid #e6edf5;
                border-radius: 20px;
            }
            QLabel[role="login_title"] {
                font-size: 28px;
                font-weight: 700;
                color: #0f172a;
                background: transparent;
            }
            QLabel[role="login_subtitle"] {
                font-size: 14px;
                color: #64748b;
                background: transparent;
            }
            QLineEdit {
                background: #ffffff;
                border: 1px solid #d6dee8;
                border-radius: 10px;
                padding: 10px 12px;
                min-height: 22px;
            }
            QLineEdit:focus {
                border: 1px solid #1677ff;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #1677ff, stop:1 #4096ff);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 18px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #0f67e6, stop:1 #2f86f6);
            }
        """)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(50, 36, 50, 36)
        root_layout.setSpacing(0)

        root_layout.addStretch()

        card = QFrame()
        card.setObjectName("loginCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(38, 34, 38, 34)
        card_layout.setSpacing(20)

        title = QLabel("基于图像识别的工业缺陷检测系统")
        title.setProperty("role", "login_title")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("请输入账号和密码登录系统")
        subtitle.setProperty("role", "login_subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(20, 10, 20, 10)
        form_layout.setHorizontalSpacing(18)
        form_layout.setVerticalSpacing(18)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.user_name = QLineEdit()
        self.u_password = QLineEdit()
        self.user_name.setPlaceholderText("请输入账号")
        self.u_password.setPlaceholderText("请输入密码")
        self.user_name.setEchoMode(QLineEdit.Normal)
        self.u_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("账 号：", self.user_name)
        form_layout.addRow("密 码：", self.u_password)

        login_button = QPushButton("登录")
        login_button.clicked.connect(self.login)
        login_button.setCursor(Qt.PointingHandCursor)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(form_widget)
        card_layout.addWidget(login_button)

        root_layout.addWidget(card)
        root_layout.addStretch()

        self.mainWindow = MainWindow()
        self.setFont(font_title)

    def login(self):
        user_name = self.user_name.text()
        pwd = self.u_password.text()
        is_ok = (user_name == USERNAME) and (pwd == PASSWORD)

        print(is_ok)
        if is_ok:
            self.mainWindow.show()
            self.close()
        else:
            QMessageBox.warning(self, "账号密码不匹配", "请输入正确的账号密码")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = LoginWindow()
    mainWindow.show()
    sys.exit(app.exec())
