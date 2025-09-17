import torch
from torch import nn
from torchvision.models import (
    resnet18, resnet34, resnet50,resnet101, resnet152,  # 导入支持的ResNet模型类
    ResNet18_Weights, ResNet34_Weights, ResNet50_Weights, ResNet101_Weights, ResNet152_Weights  # 导入对应模型的权重类
)
import os

class CNN(nn.Module):
    def __init__(self, num_classes: int = 12) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(256 * 16 * 16, 4096),
        )
        self.fc = nn.Sequential(
            nn.ReLU(),
            nn.Linear(4096, 2048),
            nn.ReLU(),
            nn.Linear(2048, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        # x = torch.flatten(x, 1)
        x = self.fc(x)
        return x


# -------------------------- 核心重构：支持多ResNet模型创建的通用函数 --------------------------
def create_resnet(
        model_name: str = "resnet50",  # 新增：模型名称（支持resnet34/resnet50）
        num_classes: int = 1000,  # 目标分类数（默认1000，匹配官方预训练）
        weight_path: str = None  # 本地权重路径（非空则覆盖官方权重）
) -> nn.Module:
    """
    通用ResNet模型创建函数，支持自动匹配模型名称与权重：
    1. 支持模型：resnet34、resnet50（可扩展至其他ResNet系列）
    2. 核心流程：根据模型名称加载对应官方权重→失败则降级随机初始化→本地权重覆盖→分类头适配
    """
    # 1. 模型与权重的映射字典（关键：通过名称关联模型类、权重类、特征维度）
    #    结构：{模型名称: (模型类, 权重类)}
    resnet_map = {
        "resnet18": (resnet18, ResNet18_Weights),
        "resnet34": (resnet34, ResNet34_Weights),
        "resnet50": (resnet50, ResNet50_Weights),
        "resnet101": (resnet101, ResNet101_Weights),
        "resnet152": (resnet152, ResNet152_Weights),
    }

    # 2. 校验模型名称合法性（不支持则报错）
    if model_name not in resnet_map:
        supported_models = ", ".join(resnet_map.keys())
        raise ValueError(f"不支持的模型名称：{model_name}，仅支持{supported_models}")

    # 3. 根据模型名称获取对应的模型类和权重类
    model_cls, weights_cls = resnet_map[model_name]

    # 4. 尝试加载对应模型的官方预训练权重（优先）
    try:
        # 加载对应模型的ImageNet1K官方权重（统一用V1稳定版本）
        official_weights = weights_cls.IMAGENET1K_V1
        model = model_cls(weights=official_weights)
        print('已创建官方权重的模型')
    except Exception as e:
        # 官方权重加载失败（网络/文件问题），降级为随机初始化模型
        model = model_cls(weights=None)
        print(f'出现错误无法加载官方模型, 已创建无权重模型')

    # 5. 有本地权重→适配并覆盖加载（逻辑与原代码一致，兼容不同ResNet）
    if weight_path is not None:
        if not os.path.isfile(weight_path):
            raise FileNotFoundError(f"本地权重文件不存在：{weight_path}")

        try:
            local_weights = torch.load(weight_path, weights_only=True, map_location='cpu')

            # 验证权重完整性（必须包含fc层参数，所有ResNet均用"fc.weight"键）
            if 'fc.weight' not in local_weights:
                raise KeyError(f"{model_name} 本地权重缺失'fc.weight'键，非完整权重")

            # 从本地权重提取分类数（所有ResNet的fc层权重形状均为[out_features, in_features]）
            weight_num_class = local_weights['fc.weight'].shape[0]

            # 适配模型fc层（所有ResNet均通过model.fc.in_features获取输入维度）
            in_features = model.fc.in_features
            model.fc = nn.Linear(in_features, weight_num_class)

            # 加载本地权重覆盖现有模型（strict=True确保完全匹配）
            model.load_state_dict(local_weights, strict=True)
            print(f'已加载{weight_path}的权重')

        except Exception as e:
            raise RuntimeError(f"{model_name} 本地权重处理失败：{str(e)}") from e

    # 6. 无本地权重→按num_class调整分类头（逻辑不变，兼容不同ResNet）
    else:
        if num_classes != 1000:
            in_features = model.fc.in_features
            model.fc = nn.Linear(in_features, num_classes)

    return model

