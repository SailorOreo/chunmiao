import os
import random
import shutil

random.seed(42)  # 保证可复现

# 数据集路径
images_dir = "NEU-DET_2/images"
labels_dir = "NEU-DET_2/labels"

# 输出路径
output_dir = "NEU-DET_split"

# 创建训练集和验证集文件夹
for split in ["trainimages", "val"]:
    os.makedirs(os.path.join(output_dir, split, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, split, "labels"), exist_ok=True)

# 类别列表
classes = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']

# 按类别分组
category_files = {c: [] for c in classes}
for f in os.listdir(images_dir):
    if f.endswith(".jpg"):
        for c in classes:
            if f.startswith(c + "_"):
                category_files[c].append(f)
                break

# 分层随机划分
train_files = []
val_files = []

for c in classes:
    files = category_files[c]
    random.shuffle(files)
    n_total = len(files)
    n_train = int(n_total * 0.8)  # 训练集80%
    train_files.extend(files[:n_train])
    val_files.extend(files[n_train:])

print(f"总训练集: {len(train_files)} 张, 总验证集: {len(val_files)} 张")

# 函数：复制图片和标签
def copy_files(file_list, split):
    for f in file_list:
        # 图片
        shutil.copy(os.path.join(images_dir, f),
                    os.path.join(output_dir, split, "images", f))
        # 标签
        txt_file = f.replace(".jpg", ".txt")
        shutil.copy(os.path.join(labels_dir, txt_file),
                    os.path.join(output_dir, split, "labels", txt_file))

# 执行复制
copy_files(train_files, "trainimages")
copy_files(val_files, "val")

print("分层随机划分完成！")