from ultralytics import YOLO
from ultralytics.utils.plotting import plot_images
import torch

# 加载模型与数据集
model = YOLO("runs/detect/train/weights/best.pt")
dataset = model.val(data="GC-10DET.yaml", imgsz=640).dataloader

# 取1个批次的样本
batch = next(iter(dataset))
img, gt_boxes, gt_cls = batch["img"], batch["bboxes"], batch["cls"]

# 模型推理获取预测结果
preds = model(img, verbose=False)

# 绘制真实标签图
gt_plot = plot_images(img, gt_boxes, gt_cls, names=model.names)
# 绘制预测结果图
pred_plot = plot_images(img, [p.boxes.data for p in preds], names=model.names)

# 保存图片
from PIL import Image
Image.fromarray(gt_plot[..., ::-1]).save("val_batch_custom_labels.jpg")
Image.fromarray(pred_plot[..., ::-1]).save("val_batch_custom_pred.jpg")