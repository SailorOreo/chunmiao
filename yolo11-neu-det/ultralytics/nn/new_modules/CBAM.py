import torch
import torch.nn as nn

class ChannelAttention(nn.Module):
    def __init__(self, in_channels, reduction=16):
        """
        通道注意力模块
        Args:
            in_channels (int): 输入通道数
            reduction (int): 缩减比例因子
        """
        super(ChannelAttention, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)  # 全局平均池化
        self.max_pool = nn.AdaptiveMaxPool2d(1)  # 全局最大池化

        self.fc = nn.Sequential(
            nn.Linear(in_channels, in_channels // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(in_channels // reduction, in_channels, bias=False)
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        batch, channels, _, _ = x.size()

        # 全局平均池化
        avg_out = self.fc(self.avg_pool(x).view(batch, channels))
        # 全局最大池化
        max_out = self.fc(self.max_pool(x).view(batch, channels))

        # 加和后通过 Sigmoid
        out = avg_out + max_out
        out = self.sigmoid(out).view(batch, channels, 1, 1)

        # 通道加权
        return x * out


class SpatialAttention(nn.Module):
    def __init__(self, kernel_size=7):
        """
        空间注意力模块
        Args:
            kernel_size (int): 卷积核大小
        """
        super(SpatialAttention, self).__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size=kernel_size, padding=kernel_size // 2, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # 通道维度求平均和最大值
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        combined = torch.cat([avg_out, max_out], dim=1)  # 拼接

        # 卷积处理
        out = self.conv(combined)
        out = self.sigmoid(out)

        # 空间加权
        return x * out


class CBAM(nn.Module):
    def __init__(self, in_channels, reduction=16, kernel_size=7):
        """
        CBAM 模块
        Args:
            in_channels (int): 输入通道数
            reduction (int): 缩减比例因子
            kernel_size (int): 空间注意力卷积核大小
        """
        super(CBAM, self).__init__()
        self.channel_attention = ChannelAttention(in_channels, reduction)
        self.spatial_attention = SpatialAttention(kernel_size)

    def forward(self, x):
        # 通道注意力模块
        x = self.channel_attention(x)
        # 空间注意力模块
        x = self.spatial_attention(x)
        return x
