import os
import cv2
import albumentations as A
from tqdm import tqdm


# 数据增强脚本
def augment_images_and_labels(img_dir, label_dir, output_img_dir, output_label_dir, val_img_dir, val_label_dir,
                              augment_times=3):
    """
    对YOLO数据进行安全的数据增强。
    :param img_dir: 原始图片的目录路径
    :param label_dir: YOLO标签目录路径
    :param output_img_dir: 增强后的图片保存目录
    :param output_label_dir: 增强后的标签保存目录
    :param val_img_dir: 第一个增强图片存放的目录，用于验证集
    :param val_label_dir: 第一个增强标签存放的目录，用于验证集
    :param augment_times: 每张图片的增强次数
    """
    # 确保输出目录存在
    os.makedirs(output_img_dir, exist_ok=True)
    os.makedirs(output_label_dir, exist_ok=True)
    os.makedirs(val_img_dir, exist_ok=True)
    os.makedirs(val_label_dir, exist_ok=True)

    # 遍历图片和标签
    for img_file in tqdm(os.listdir(img_dir)):
        if not img_file.endswith(('.jpg', '.png', '.jpeg')):
            continue

        # 获取文件路径
        img_path = os.path.join(img_dir, img_file)
        label_path = os.path.join(label_dir, os.path.splitext(img_file)[0] + '.txt')

        # 读取图像
        image = cv2.imread(img_path)
        if image is None:
            print(f"无法读取图像: {img_path}")
            continue
        height, width = image.shape[:2]

        # 读取YOLO标签
        bboxes = []
        class_labels = []
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f.readlines():
                    parts = line.strip().split()
                    class_id = int(parts[0])
                    x_center, y_center, w, h = map(float, parts[1:])
                    bboxes.append([x_center, y_center, w, h])
                    class_labels.append(class_id)

        # 原始标签检查
        if not bboxes:
            print(f"标签为空: {label_path}")
            continue

        # 进行数据增强
        for i in range(augment_times):
            # 动态调整裁剪区域大小（最大不能大于图像尺寸）
            min_crop_size = min(height, width)
            crop_height = min(500, min_crop_size)
            crop_width = min(500, min_crop_size)

            # 更新增强方法中的裁剪尺寸
            augmentations = A.Compose([
                A.HorizontalFlip(p=0.5),
                A.RandomBrightnessContrast(p=0.5),
                A.Rotate(limit=10, p=0.5, border_mode=cv2.BORDER_CONSTANT),
                A.GaussianBlur(p=0.2),
                A.GaussNoise(p=0.2),
                A.Resize(width=640, height=640, p=0.5),
                A.RandomCrop(width=crop_width, height=crop_height, p=0.5),
                A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.5),
                A.ElasticTransform(p=0.2),
                A.RandomScale(p=0.2),
            ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

            augmented = augmentations(image=image, bboxes=bboxes, class_labels=class_labels)
            aug_image = augmented['image']
            aug_bboxes = augmented['bboxes']
            aug_labels = augmented['class_labels']

            # 如果是第一个增强，保存到验证集目录
            if i == 0:
                output_img_path = os.path.join(val_img_dir, f"{os.path.splitext(img_file)[0]}_aug_0.jpg")
                output_label_path = os.path.join(val_label_dir, f"{os.path.splitext(img_file)[0]}_aug_0.txt")
            else:
                # 否则，保存到训练集目录
                output_img_path = os.path.join(output_img_dir, f"{os.path.splitext(img_file)[0]}_aug_{i}.jpg")
                output_label_path = os.path.join(output_label_dir, f"{os.path.splitext(img_file)[0]}_aug_{i}.txt")

            # 保存增强后的图片
            cv2.imwrite(output_img_path, aug_image)

            # 保存增强后的标签
            with open(output_label_path, 'w') as f:
                for bbox, cls in zip(aug_bboxes, aug_labels):
                    x_center, y_center, w, h = bbox
                    f.write(f"{int(cls)} {x_center} {y_center} {w} {h}\n")

    print("数据增强完成！")


if __name__ == "__main__":
    # 输入目录路径，必须是全英文路径
    img_dir = r"D:\A01PythonProjects3123\labelImg-master\gullyYolo\images"  # 原始图片路径
    label_dir = r"D:\A01PythonProjects3123\labelImg-master\gullyYolo\labels"  # YOLO标签路径

    # 输出目录路径
    output_img_dir = "handleImages"  # 保存增强后图片路径
    output_label_dir = "handleLabels"  # 保存增强后标签路径

    # 验证集目录路径
    val_img_dir = "val_images"  # 保存增强后验证集图片路径
    val_label_dir = "val_labels"  # 保存增强后验证集标签路径

    # 执行数据增强
    augment_images_and_labels(img_dir, label_dir, output_img_dir, output_label_dir, val_img_dir, val_label_dir,
                              augment_times=8)