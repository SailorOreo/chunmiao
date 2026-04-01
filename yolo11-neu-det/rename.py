import os
import os.path as osp
folder = "runs/yolo11s_pretrained/train"
new_x = "38-heat"
files = os.listdir(folder)
for file in files:
    print(file)
    if os.path.isfile(osp.join(folder, file)):
        print(file)
        file_new_name = f"{new_x}_" + file
        file_src_path = osp.join(folder, file)
        file_new_path = osp.join(folder, file_new_name)
        os.rename(file_src_path, file_new_path)