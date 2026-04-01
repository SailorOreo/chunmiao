import cv2
import numpy as np
from pathlib import Path
from torch.utils.data import Dataset


class CustomDataset(Dataset):
    def __init__(self, data_path, img_size=640, augment=False):
        self.data_path = data_path
        self.img_size = img_size
        self.augment = augment
        self.img_paths = list(Path(data_path).glob('*.jpg'))  # 假设数据集图片为 .jpg 格式
        self.label_paths = [p.with_suffix('.txt') for p in self.img_paths]  # 假设标签是 txt 文件

    def __len__(self):
        return len(self.img_paths)

    def __getitem__(self, idx):
        img = cv2.imread(str(self.img_paths[idx]))
        img = cv2.resize(img, (self.img_size, self.img_size))  # 调整大小

        # 加载标签
        label = np.loadtxt(self.label_paths[idx], delimiter=' ')

        # 数据增强：翻转等
        if self.augment:
            if np.random.rand() > 0.5:
                img = cv2.flip(img, 1)  # 水平翻转

        # 将图像转为张量并归一化
        img = img / 255.0  # 归一化至 [0, 1]
        img = img.transpose(2, 0, 1)  # 转换为 CHW 格式

        return img, label  # 返回图像和标签

