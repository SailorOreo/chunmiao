import torch
import platform

# 硬件信息（部分需手动结合上述截图）
print("=== 硬件信息（部分）===")
print(f"CPU 型号: AMD Ryzen 9 8940HX with Radeon Graphics")
print(f"NVIDIA GPU 型号: NVIDIA GeForce RTX 5060 Laptop GPU")
print(f"NVIDIA GPU 专用内存: 8.0 GB (当前使用 7.5 GB)")
print(f"NVIDIA GPU 温度: 57℃")

# 软件环境信息
print("\n=== 软件环境信息 ===")
# Python 版本
print(f"Python 版本: {platform.python_version()}")

# PyTorch 信息
print(f"PyTorch 版本: {torch.__version__}")
print(f"CUDA 是否可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA 版本: {torch.version.cuda}")
    print(f"GPU 设备名称: {torch.cuda.get_device_name(0)}")
else:
    print("未检测到可用的 CUDA 设备（或 PyTorch 未正确配置 CUDA）")

# CUDA 版本（命令行方式提示）
print("\n提示：可通过 `nvcc --version` 或 NVIDIA 控制面板查看 CUDA 版本")