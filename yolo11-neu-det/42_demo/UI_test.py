# ********************* 配置切换界面 ****************************
config_widget = QWidget()
config_layout = QVBoxLayout(config_widget)
config_layout.setContentsMargins(24, 24, 24, 24)
config_layout.setSpacing(24)  # 增大主垂直间距

config_vid_title = self.make_title_label("配置信息修改")
config_icon_label = QLabel()
config_icon_label.setPixmap(QPixmap("images/UI/config.png"))
config_icon_label.setAlignment(Qt.AlignCenter)

config_card = CardFrame()
config_card_layout = QVBoxLayout(config_card)
config_card_layout.setContentsMargins(32, 32, 32, 32)  # 增大内边距
config_card_layout.setSpacing(20)

config_grid_widget = QWidget()
config_grid_layout = QGridLayout(config_grid_widget)
config_grid_layout.setHorizontalSpacing(24)  # 增大水平间距
config_grid_layout.setVerticalSpacing(18)    # 增大垂直间距
config_grid_layout.setContentsMargins(0, 0, 0, 0)

row = 0
# 系统图像显示大小
config_output_size_label = QLabel("系统图像显示大小")
self.config_output_size_value = QLineEdit(str(self.output_size))
self.config_output_size_value.setMinimumHeight(28)
config_grid_layout.addWidget(config_output_size_label, row, 0)
config_grid_layout.addWidget(self.config_output_size_value, row, 1)
row += 1

# 摄像头源地址
config_vid_source_label = QLabel("摄像头源地址")
self.config_vid_source_value = QLineEdit(str(self.vid_source))
self.config_vid_source_value.setMinimumHeight(28)
config_grid_layout.addWidget(config_vid_source_label, row, 0)
config_grid_layout.addWidget(self.config_vid_source_value, row, 1)
row += 1

# 视频帧保存间隔
config_vid_gap_label = QLabel("视频帧保存间隔")
self.config_vid_gap_value = QLineEdit(str(self.vid_gap))
self.config_vid_gap_value.setMinimumHeight(28)
config_grid_layout.addWidget(config_vid_gap_label, row, 0)
config_grid_layout.addWidget(self.config_vid_gap_value, row, 1)
row += 1

# 检测模型置信度阈值
config_conf_thres_label = QLabel("检测模型置信度阈值")
self.config_conf_thres_value = QLineEdit(str(self.conf_thres))
self.config_conf_thres_value.setMinimumHeight(28)
config_grid_layout.addWidget(config_conf_thres_label, row, 0)
config_grid_layout.addWidget(self.config_conf_thres_value, row, 1)
row += 1

# 检测模型IOU阈值
config_iou_thres_label = QLabel("检测模型IOU阈值")
self.config_iou_thres_value = QLineEdit(str(self.iou_thres))
self.config_iou_thres_value.setMinimumHeight(28)
config_grid_layout.addWidget(config_iou_thres_label, row, 0)
config_grid_layout.addWidget(self.config_iou_thres_value, row, 1)
row += 1

# 推理时是否保存txt文件
config_save_txt_label = QLabel("推理时是否保存txt文件")
self.config_save_txt_value = QRadioButton("True")
self.config_save_txt_value.setChecked(False)
self.config_save_txt_value.setMinimumHeight(28)
self.config_save_txt_value.setAutoExclusive(False)
config_grid_layout.addWidget(config_save_txt_label, row, 0)
config_grid_layout.addWidget(self.config_save_txt_value, row, 1)
row += 1

# 推理时是否保存置信度
config_save_conf_label = QLabel("推理时是否保存置信度")
self.config_save_conf_value = QRadioButton("True")
self.config_save_conf_value.setChecked(False)
self.config_save_conf_value.setMinimumHeight(28)
self.config_save_conf_value.setAutoExclusive(False)
config_grid_layout.addWidget(config_save_conf_label, row, 0)
config_grid_layout.addWidget(self.config_save_conf_value, row, 1)
row += 1

# 推理时是否保存切片文件
config_save_crop_label = QLabel("推理时是否保存切片文件")
self.config_save_crop_value = QRadioButton("True")
self.config_save_crop_value.setChecked(False)
self.config_save_crop_value.setMinimumHeight(28)
self.config_save_crop_value.setAutoExclusive(False)
config_grid_layout.addWidget(config_save_crop_label, row, 0)
config_grid_layout.addWidget(self.config_save_crop_value, row, 1)
row += 1

# 追踪配置
config_track_label = QLabel("追踪配置")
self.config_track_value = QComboBox(self)
self.config_track_value.addItems(['不开启追踪', "bytetrack.yaml", "botsort.yaml"])
self.config_track_value.setMinimumHeight(28)
config_grid_layout.addWidget(config_track_label, row, 0)
config_grid_layout.addWidget(self.config_track_value, row, 1)

# 保存按钮
save_config_button = QPushButton("保存配置信息")
save_config_button.setFont(QFont('Microsoft YaHei', 11))
save_config_button.clicked.connect(self.save_config_change)

config_card_layout.addWidget(config_icon_label)
config_card_layout.addWidget(config_grid_widget)
config_card_layout.addWidget(save_config_button)

config_layout.addWidget(config_vid_title)
config_layout.addWidget(config_card)