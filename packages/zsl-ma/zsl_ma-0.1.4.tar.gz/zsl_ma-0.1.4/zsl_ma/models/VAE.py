import torch
import torch.nn as nn
import torch.nn.functional as F


# class ResidualBlock(nn.Module):
#     def __init__(self, channels):
#         super().__init__()
#         # 优化1：使用更高效的残差结构
#         self.res = nn.Sequential(
#             nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False),
#             nn.BatchNorm2d(channels),
#             nn.ReLU(inplace=True),  # inplace节省内存
#             nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False),
#             nn.BatchNorm2d(channels)
#         )
#         self.final_activation = nn.ReLU(inplace=True)
#
#     def forward(self, x):
#         # 优化2：更简洁的残差连接
#         return self.final_activation(self.res(x) + x)
#
#
# class Encoder(nn.Module):
#     def __init__(self, mask_ratio=0.3, input_size=32):
#         super().__init__()
#         self.noise_std = mask_ratio
#         self.input_size = input_size
#
#         # 优化3：创建可复用的下采样模块
#         def create_downsample_block(in_c, out_c, stride=2):
#             return nn.Sequential(
#                 nn.Conv2d(in_c, out_c, 3, stride, 1, bias=False),
#                 nn.BatchNorm2d(out_c),
#                 nn.ReLU(inplace=True),
#                 ResidualBlock(out_c)
#             )
#
#         # 优化4：自动计算最终特征图尺寸
#         self.feature_size = input_size // 8  # 三次2倍下采样
#         self.channels = 128
#
#         self.blocks = nn.Sequential(
#             create_downsample_block(3, 16),  # 32x32 -> 16x16
#             create_downsample_block(16, 32),  # 16x16 -> 8x8
#             create_downsample_block(32, 64),  # 8x8 -> 4x4
#             nn.Sequential(  # 最终特征提取（无下采样）
#                 nn.Conv2d(64, self.channels, 3, 1, 1, bias=False),
#                 nn.BatchNorm2d(self.channels),
#                 nn.ReLU(inplace=True),
#                 ResidualBlock(self.channels)
#             )
#         )
#
#         # 优化5：动态计算全连接层输入尺寸
#         self.fc_in_features = self.channels * self.feature_size * self.feature_size
#         self.fc = nn.Linear(self.fc_in_features, 1024)
#
#     def add_noise(self, x):
#         if self.training and self.noise_std > 0:
#             # 生成与输入相同形状的噪声
#             noise = torch.randn_like(x) * self.noise_std
#             # 将噪声添加到输入
#             noisy_x = x + noise
#
#             # 确保值在[0,1]范围内
#             # 如果输入是归一化的图像，这很重要
#             return torch.clamp(noisy_x, 0, 1)
#         return x
#
#     def forward(self, x):
#         x = self.add_noise(x)
#         x = self.blocks(x)
#         x = x.view(x.size(0), -1)  # 替代Flatten，更高效
#         return self.fc(x)
#
#
# class Decoder(nn.Module):
#     def __init__(self, feature_size=4, channels=128):
#         super().__init__()
#         self.feature_size = feature_size
#         self.channels = channels
#
#         # 优化7：使用更高效的上采样方法
#         self.fc = nn.Linear(1024, channels * feature_size * feature_size)
#
#         self.blocks = nn.Sequential(
#             # 上采样块1: 4x4 -> 8x8
#             self.create_upsample_block(channels, 64),
#             # 上采样块2: 8x8 -> 16x16
#             self.create_upsample_block(64, 32),
#             # 上采样块3: 16x16 -> 32x32
#             self.create_upsample_block(32, 16),
#             # 输出层
#             nn.Conv2d(16, 3, 3, padding=1)
#         )
#
#     def create_upsample_block(self, in_c, out_c):
#         return nn.Sequential(
#             nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
#             nn.Conv2d(in_c, out_c, 3, padding=1, bias=False),
#             nn.BatchNorm2d(out_c),
#             nn.ReLU(inplace=True),
#             ResidualBlock(out_c)
#         )
#
#     def forward(self, x):
#         x = self.fc(x)
#         x = x.view(x.size(0), self.channels, self.feature_size, self.feature_size)
#         return torch.sigmoid(self.blocks(x))  # 确保输出在[0,1]范围
#
#
# class CAE(nn.Module):
#     def __init__(self, input_size=64, mask_ratio=0.3):
#         super().__init__()
#         self.encoder = Encoder(mask_ratio, input_size)
#         self.decoder = Decoder(self.encoder.feature_size, self.encoder.channels)
#
#     def forward(self, x):
#         latent = self.encoder(x)
#         return self.decoder(latent)
#
#     def encode(self, x):
#         """单独提取编码特征"""
#         return self.encoder(x)
#
#     def decode(self, z):
#         """从潜在空间解码"""
#         return self.decoder(z)
#
#     def save_encoder(self, path):
#         torch.save(self.encoder.state_dict(), path)
#
#     def save_decoder(self, path):
#         torch.save(self.decoder.state_dict(), path)
#
#     def load_encoder(self, path, device='cuda'):
#         self.encoder.load_state_dict(torch.load(path, map_location=device))
#
#     def load_decoder(self, path, device='cuda'):
#         self.decoder.load_state_dict(torch.load(path, map_location=device))
#

# 定义残差块
class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.res = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
            nn.Conv2d(channels, channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
        )

    def forward(self, x):
        residual = x
        out = self.res(x)
        return out + residual


# 编码器
class Encoder(nn.Module):
    def __init__(self, mask_ratio=0):
        super().__init__()
        self.mask_ratio = mask_ratio
        # Conv1 + ResidualBlock1
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 16, 3, stride=2, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            ResidualBlock(16)
        )
        # Conv2 + ResidualBlock2
        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, 3, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            ResidualBlock(32)
        )
        # Conv3 + ResidualBlock3
        self.conv3 = nn.Sequential(
            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            ResidualBlock(64)
        )
        # Conv4 + ResidualBlock4
        self.conv4 = nn.Sequential(
            nn.Conv2d(64, 128, 3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            ResidualBlock(128)
        )
        self.flatten = nn.Flatten()
        self.fc = nn.Linear(128 * 8 * 8, 4096)

    def add_noise(self, x):
        if self.training and self.mask_ratio > 0:
            mask = (torch.rand_like(x) > self.mask_ratio).float()
            return x * mask
        return x

    def forward(self, x):
        x = self.add_noise(x)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.flatten(x)
        x = self.fc(x)
        return x


# 解码器
class Decoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(4096, 128 * 8 * 8)
        self.unFlatten = nn.Unflatten(1, (128, 8, 8))

        self.deConv = nn.Sequential(
            # DeConv1
            nn.ConvTranspose2d(128, 64, 3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            # DeConv2
            nn.ConvTranspose2d(64, 32, 3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            # DeConv3
            nn.ConvTranspose2d(32, 16, 3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            # DeConv4 (输出层)
            nn.ConvTranspose2d(16, 3, 3, stride=2, padding=1, output_padding=1),
        )

    def forward(self, x):
        x = self.fc(x)
        x = self.unFlatten(x)
        x = self.deConv(x)
        # return torch.sigmoid(x)  # 假设输出在[0,1]范围
        return x


class DRCAE(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = Encoder()
        self.decoder = Decoder()

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

    def save_encoder(self, path):
        torch.save(self.encoder.state_dict(), path)



if __name__ == '__main__':
    model = DRCAE()
    x = torch.randn(1, 3, 64, 64)
    y = model(x)
    print(y.shape)
