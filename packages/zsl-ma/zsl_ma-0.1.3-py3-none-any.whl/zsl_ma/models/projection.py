import torch
import torch.nn.functional as F
from torch import nn
from torch.nn.init import kaiming_normal_

from zsl_ma.models.CNN import CNN, create_resnet
from zsl_ma.models.DisentangledModel import DisentangledModel
from zsl_ma.models.kan import KAN


# 1. 语义属性投影模型
# class AttributeProjectionModel(nn.Module):
#     def __init__(self, attr_dim=128, embed_dim=512):
#         super().__init__()
#         # self.hidden = int(attr_dim / 2)
#         # 属性投影分支
#         self.attr_projector = nn.Sequential(
#             nn.Linear(attr_dim, 256),
#             nn.ReLU(),
#             nn.Linear(256, embed_dim),
#             # nn.ReLU(),
#             # nn.Linear(64, embed_dim)
#         )
#
#     def forward(self, attr):
#         # 处理属性输入
#         attr_embed = self.attr_projector(attr)
#         return attr_embed

# class AttributeProjectionModel(nn.Module):
#     def __init__(self, attr_dim=128, embed_dim=512, num_classes=10, ortho_weight=100, reg_method='euclidean',
#                  margin=100.0):
#         self.ortho_weight = ortho_weight
#         self.reg_method = reg_method  # 正则化方法选择
#         self.margin = margin
#         super().__init__()
#         # self.hidden = int(attr_dim / 2)
#         # 属性投影分支
#         self.attr_projector = nn.Sequential(
#             nn.Linear(attr_dim, 256),
#             nn.BatchNorm1d(256),
#             nn.Dropout(0.5),
#             nn.ReLU(),
#             nn.Linear(256, 512),
#             nn.BatchNorm1d(512),
#             nn.Dropout(0.5),
#             nn.ReLU(),
#             nn.Linear(512, 1024),
#             nn.BatchNorm1d(1024),
#             nn.Dropout(0.5),
#             nn.ReLU(),
#             nn.Linear(1024, 2048),
#             nn.BatchNorm1d(2048),
#             nn.Dropout(0.5),
#             nn.ReLU(),
#             # nn.Linear(2048, embed_dim),
#             # KAN([2048, 1024, embed_dim], scale_noise=0),
#         )
#         self.fc = nn.Sequential(
#             nn.ReLU(),
#             nn.Linear(embed_dim, num_classes),
#         )
#
#     def forward(self, attr):
#         # 处理属性输入
#         attr_embed = self.attr_projector(attr)
#         x = self.fc(attr_embed)
#         return attr_embed, x
#
#     def orthogonal_regularization(self, features, labels):
#         """
#         特征解耦正则化 - 根据选择的reg_method调用不同的实现
#         """
#         if self.reg_method == 'cosine':
#             return self._cosine_regularization(features, labels)
#         elif self.reg_method == 'euclidean':
#             return self._euclidean_regularization(features, labels)
#         elif self.reg_method == 'center':
#             return self._center_regularization(features, labels)
#         elif self.reg_method == 'inter_branch':
#             return self._inter_branch_regularization(features)
#         else:
#             raise ValueError(f"Unknown regularization method: {self.reg_method}")
#
#     def _cosine_regularization(self, features, labels):
#         """
#         基于余弦相似度的正则化（原始方法）：
#         - 同一属性内,标签相同的样本特征尽可能相近
#         - 同一属性内,标签不同的样本特征尽可能远离
#         """
#         batch_size = features.size(0)
#         if batch_size <= 1:
#             return 0.0
#
#         # 特征L2归一化,使点积等价于余弦相似度
#         normalized_feats = F.normalize(features, p=2, dim=1)
#
#         # 计算所有样本对的相似度矩阵
#         sim_matrix = torch.matmul(normalized_feats, normalized_feats.T)
#
#         # 创建标签匹配矩阵
#         label_eq_matrix = (labels.unsqueeze(0) == labels.unsqueeze(1)).float()
#         mask = 1 - torch.eye(batch_size, device=features.device)
#         label_eq_matrix = label_eq_matrix * mask
#         label_ne_matrix = (1 - label_eq_matrix) * mask
#
#         # 同标签损失：相似度应接近1
#         same_label_loss = torch.mean((1 - sim_matrix) * label_eq_matrix)
#
#         # 异标签损失：相似度应接近-1
#         diff_label_loss = torch.mean((1 + sim_matrix) * label_ne_matrix)
#
#         return self.ortho_weight * (same_label_loss + diff_label_loss)
#
#     def _euclidean_regularization(self, features, labels):
#         """
#         基于欧几里得距离的正则化：
#         - 同一属性内,标签相同的样本特征距离尽可能小
#         - 同一属性内,标签不同的样本特征距离尽可能大
#         """
#         batch_size = features.size(0)
#         if batch_size <= 1:
#             return 0.0
#
#         # 计算所有样本对之间的欧几里得距离平方
#         norms = torch.sum(features ** 2, dim=1)
#         dist_matrix = norms.unsqueeze(0) + norms.unsqueeze(1) - 2 * torch.matmul(features, features.T)
#
#         # 创建标签匹配矩阵
#         label_eq_matrix = (labels.unsqueeze(0) == labels.unsqueeze(1)).float()
#         mask = 1 - torch.eye(batch_size, device=features.device)
#         label_eq_matrix = label_eq_matrix * mask
#         label_ne_matrix = (1 - label_eq_matrix) * mask
#
#         # 同标签损失：距离应接近0
#         same_label_loss = torch.mean(dist_matrix * label_eq_matrix)
#
#         # 异标签损失：距离应尽可能大,使用边际损失
#         # margin = 10.0
#         diff_label_loss = torch.mean(torch.clamp(self.margin - dist_matrix, min=0) * label_ne_matrix)
#
#         return self.ortho_weight * (same_label_loss + diff_label_loss)
#
#     def _center_regularization(self, features, labels):
#         """
#         基于类别中心的正则化：
#         - 同一属性内,样本特征尽可能接近其类别中心
#         - 同一属性内,不同类别的中心尽可能远离
#         """
#         unique_labels = torch.unique(labels)
#         if len(unique_labels) <= 1:
#             return 0.0
#
#         # 计算每个类别的中心
#         centers = []
#         for label in unique_labels:
#             mask = (labels == label)
#             if torch.sum(mask) > 0:
#                 center = torch.mean(features[mask], dim=0)
#                 centers.append(center)
#
#         if len(centers) <= 1:
#             return 0.0
#
#         centers = torch.stack(centers)
#
#         # 类内损失：样本到其类别中心的距离
#         intra_loss = 0.0
#         for i, label in enumerate(unique_labels):
#             mask = (labels == label)
#             if torch.sum(mask) > 0:
#                 class_features = features[mask]
#                 center = centers[i]
#                 distances = torch.norm(class_features - center, dim=1)
#                 intra_loss += torch.mean(distances)
#
#         intra_loss /= len(unique_labels)
#
#         # 类间损失：类别中心之间的距离
#         inter_loss = 0.0
#         num_pairs = 0
#         for i in range(len(centers)):
#             for j in range(i + 1, len(centers)):
#                 distance = torch.norm(centers[i] - centers[j])
#                 margin = 5.0
#                 inter_loss += torch.clamp(margin - distance, min=0)
#                 num_pairs += 1
#
#         if num_pairs > 0:
#             inter_loss /= num_pairs
#         else:
#             inter_loss = 0.0
#
#         return self.ortho_weight * (intra_loss + inter_loss)
#
#     def _inter_branch_regularization(self, features_list):
#         """
#         分支间正交正则化：
#         - 确保不同分支提取的特征相互正交
#         - 不依赖于标签信息
#         """
#         reg_loss = 0.0
#         num_branches = len(features_list)
#
#         for i in range(num_branches):
#             for j in range(i + 1, num_branches):
#                 # 归一化特征
#                 feat_i = F.normalize(features_list[i], p=2, dim=1)
#                 feat_j = F.normalize(features_list[j], p=2, dim=1)
#
#                 # 计算相关性矩阵
#                 correlation = torch.matmul(feat_i.T, feat_j)
#
#                 # 计算非对角线元素的和（希望它们接近0）
#                 reg_loss += torch.sum(correlation ** 2) - torch.sum(torch.diag(correlation) ** 2)
#
#         return self.ortho_weight * reg_loss / (num_branches * (num_branches - 1) / 2)

# class AttributeProjectionModel(nn.Module):
#     def __init__(self, attr_dim=128, embed_dim=512, num_classes=10, ortho_weight=10.0,
#                  reg_method='center', margin=10.0, contrastive_weight=0.5):
#         super().__init__()
#         self.ortho_weight = ortho_weight  # 正则化权重
#         self.reg_method = reg_method  # 特征解耦正则化方法
#         self.margin = nn.Parameter(torch.tensor(margin))  # 可学习的边际参数
#         self.contrastive_weight = contrastive_weight  # 对比损失权重
#         self.embed_dim = embed_dim
#
#         # 1. 改进的属性投影网络（加入残差连接和LayerNorm，增强特征表达）
#         self.attr_projector = nn.Sequential(
#             nn.Linear(attr_dim, 1024),
#             nn.LayerNorm(1024),  # 替代BatchNorm，小批量更稳定
#             nn.LeakyReLU(0.1),  # 避免ReLU死亡神经元问题
#             nn.Dropout(0.3),  # 降低过拟合风险
#
#             ResidualBlock(1024, 1024),  # 残差块增强特征学习
#             ResidualBlock(1024, 512),
#
#             nn.Linear(512, embed_dim),
#             nn.LayerNorm(embed_dim),  # 输出特征归一化前的稳定层
#         )
#
#         # 2. 分类头（简化结构，避免特征稀释）
#         self.fc = nn.Linear(embed_dim, num_classes)
#
#         # 初始化参数（促进更好的收敛）
#         self._initialize_weights()
#
#     def _initialize_weights(self):
#         """使用He初始化，适合ReLU/LeakyReLU激活函数"""
#         for m in self.modules():
#             if isinstance(m, nn.Linear):
#                 kaiming_normal_(m.weight, mode='fan_in', nonlinearity='leaky_relu')
#                 if m.bias is not None:
#                     nn.init.constant_(m.bias, 0)
#
#     def forward(self, attr):
#         # 投影得到特征并进行L2归一化（增强距离度量稳定性）
#         attr_embed = self.attr_projector(attr)
#         attr_embed = F.normalize(attr_embed, p=2, dim=1)  # 特征归一化
#         logits = self.fc(attr_embed)
#         return attr_embed, logits
#
#     def orthogonal_regularization(self, features, labels):
#         """增强版特征解耦正则化，优先使用类别中心方法"""
#         if self.reg_method == 'center':
#             return self._enhanced_center_regularization(features, labels)
#         elif self.reg_method == 'contrastive':
#             return self._contrastive_regularization(features, labels)
#         elif self.reg_method == 'cosine':
#             return self._cosine_regularization(features, labels)
#         elif self.reg_method == 'euclidean':
#             return self._euclidean_regularization(features, labels)
#         else:
#             raise ValueError(f"Unknown regularization method: {self.reg_method}")
#
#     def _enhanced_center_regularization(self, features, labels):
#         """增强的类别中心正则化：
#         1. 类内特征聚集（缩小类内距离）
#         2. 类间中心分散（拉大类间距离，使用动态margin）
#         """
#         unique_labels = torch.unique(labels)
#         if len(unique_labels) <= 1:
#             return 0.0
#
#         # 计算每个类别的中心（带权重的均值，降低异常值影响）
#         centers = []
#         for label in unique_labels:
#             mask = (labels == label)
#             class_feats = features[mask]
#             # 权重与距离中心的距离成反比（降低异常值权重）
#             weights = F.softmax(-torch.norm(class_feats - class_feats.mean(dim=0), dim=1), dim=0)
#             weighted_center = torch.sum(class_feats * weights.unsqueeze(1), dim=0)
#             centers.append(weighted_center)
#         centers = torch.stack(centers)  # [C, embed_dim]
#
#         # 1. 类内损失：特征到中心的距离（L2距离）
#         intra_loss = 0.0
#         for i, label in enumerate(unique_labels):
#             mask = (labels == label)
#             if mask.sum() == 0:
#                 continue
#             class_feats = features[mask]
#             intra_dist = torch.norm(class_feats - centers[i].unsqueeze(0), dim=1).mean()
#             intra_loss += intra_dist
#         intra_loss /= len(unique_labels)
#
#         # 2. 类间损失：中心之间的距离（使用动态margin）
#         inter_loss = 0.0
#         num_pairs = 0
#         for i in range(len(centers)):
#             for j in range(i + 1, len(centers)):
#                 dist = torch.norm(centers[i] - centers[j])
#                 # 动态margin：基于类别数量调整（样本多的类允许更大的margin）
#                 dynamic_margin = self.margin * (len(unique_labels) / (len(centers) - 1))
#                 inter_loss += torch.clamp(dynamic_margin - dist, min=0)
#                 num_pairs += 1
#         inter_loss /= num_pairs if num_pairs > 0 else 1
#
#         return self.ortho_weight * (intra_loss + inter_loss)
#
#     def _contrastive_regularization(self, features, labels):
#         """对比损失：直接优化同类相近、异类远离"""
#         batch_size = features.size(0)
#         if batch_size <= 1:
#             return 0.0
#
#         # 计算相似度矩阵（余弦相似度）
#         sim_matrix = F.cosine_similarity(features.unsqueeze(1), features.unsqueeze(0), dim=2)
#         mask = 1 - torch.eye(batch_size, device=features.device)  # 排除自身
#
#         # 同类对和异类对掩码
#         same_mask = (labels.unsqueeze(0) == labels.unsqueeze(1)) * mask
#         diff_mask = (labels.unsqueeze(0) != labels.unsqueeze(1)) * mask
#
#         # 同类损失：相似度应接近1
#         same_loss = (1 - sim_matrix) * same_mask
#         same_loss = same_loss.sum() / (same_mask.sum() + 1e-8)  # 归一化
#
#         # 异类损失：相似度应小于margin
#         diff_loss = torch.clamp(sim_matrix - self.margin, min=0) * diff_mask
#         diff_loss = diff_loss.sum() / (diff_mask.sum() + 1e-8)  # 归一化
#
#         return self.ortho_weight * (same_loss + diff_loss)
#
#     def _cosine_regularization(self, features, labels):
#         """保留原始余弦正则化（用于对比）"""
#         batch_size = features.size(0)
#         if batch_size <= 1:
#             return 0.0
#         normalized_feats = F.normalize(features, p=2, dim=1)
#         sim_matrix = torch.matmul(normalized_feats, normalized_feats.T)
#         label_eq_matrix = (labels.unsqueeze(0) == labels.unsqueeze(1)).float()
#         mask = 1 - torch.eye(batch_size, device=features.device)
#         label_eq_matrix *= mask
#         label_ne_matrix = (1 - label_eq_matrix) * mask
#         same_label_loss = torch.mean((1 - sim_matrix) * label_eq_matrix)
#         diff_label_loss = torch.mean((1 + sim_matrix) * label_ne_matrix)
#         return self.ortho_weight * (same_label_loss + diff_label_loss)
#
#     def _euclidean_regularization(self, features, labels):
#         """保留原始欧氏距离正则化（用于对比）"""
#         batch_size = features.size(0)
#         if batch_size <= 1:
#             return 0.0
#         norms = torch.sum(features ** 2, dim=1)
#         dist_matrix = norms.unsqueeze(0) + norms.unsqueeze(1) - 2 * torch.matmul(features, features.T)
#         label_eq_matrix = (labels.unsqueeze(0) == labels.unsqueeze(1)).float()
#         mask = 1 - torch.eye(batch_size, device=features.device)
#         label_eq_matrix *= mask
#         label_ne_matrix = (1 - label_eq_matrix) * mask
#         same_label_loss = torch.mean(dist_matrix * label_eq_matrix)
#         diff_label_loss = torch.mean(torch.clamp(self.margin - dist_matrix, min=0) * label_ne_matrix)
#         return self.ortho_weight * (same_label_loss + diff_label_loss)
#
#     def get_loss(self, attr_embed, logits, labels):
#         """整合分类损失和正则化损失"""
#         ce_loss = F.cross_entropy(logits, labels)  # 分类损失
#         reg_loss = self.orthogonal_regularization(attr_embed, labels)  # 特征正则化损失
#         total_loss = ce_loss + reg_loss
#         return total_loss, ce_loss, reg_loss
#
#
class ResidualBlock(nn.Module):
    """残差块：解决深层网络梯度消失问题，增强特征复用"""

    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.fc1 = nn.Linear(in_dim, out_dim)
        self.ln1 = nn.LayerNorm(out_dim)
        self.act = nn.LeakyReLU(0.1)
        self.fc2 = nn.Linear(out_dim, out_dim)
        self.ln2 = nn.LayerNorm(out_dim)
        # 残差连接维度适配
        self.shortcut = nn.Linear(in_dim, out_dim) if in_dim != out_dim else nn.Identity()

    def forward(self, x):
        residual = self.shortcut(x)
        x = self.fc1(x)
        x = self.ln1(x)
        x = self.act(x)
        x = self.fc2(x)
        x = self.ln2(x)
        x += residual  # 残差连接
        return self.act(x)


# 属性投影模型（不含分类损失）
class AttributeProjectionModel(nn.Module):
    def __init__(self, attr_dim=128, embed_dim=512, num_classes=10,
                 ortho_weight=15.0, triplet_weight=7.0,
                 reg_method='euclidean', margin=10.0):
        super().__init__()
        self.ortho_weight = ortho_weight  # 正则化权重
        self.triplet_weight = triplet_weight  # 三元组损失权重
        self.reg_method = reg_method  # 特征解耦正则化方法
        self.margin = nn.Parameter(torch.tensor(margin))  # 可学习的边际参数
        # self.margin = margin
        self.embed_dim = embed_dim

        # 属性投影网络
        self.attr_projector = nn.Sequential(
            nn.Linear(attr_dim, 2048),
            nn.LayerNorm(2048),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.3),

            ResidualBlock(2048, 2048),
            ResidualBlock(2048, 1024),
            ResidualBlock(1024, 512),

            nn.Linear(512, embed_dim),
            nn.LayerNorm(embed_dim),
        )

        # 保留分类头（用于评估，不参与损失计算）
        self.fc = nn.Linear(embed_dim, num_classes)

        # 初始化参数
        self._initialize_weights()

    def _initialize_weights(self):
        """使用He初始化，适合ReLU/LeakyReLU激活函数"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                kaiming_normal_(m.weight, mode='fan_in', nonlinearity='leaky_relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def forward(self, attr):
        # 投影得到特征并进行L2归一化
        attr_embed = self.attr_projector(attr)
        attr_embed = F.normalize(attr_embed, p=2, dim=1)  # 特征归一化
        logits = self.fc(attr_embed)  # 分类输出（仅用于评估）
        return attr_embed, logits

    def orthogonal_regularization(self, features, labels):
        """计算并返回总损失（仅包含特征正则化相关损失）"""
        # 1. 根据选择的正则化方法计算基础正则化损失
        if self.reg_method == 'center':
            reg_loss = self._enhanced_center_regularization(features, labels)
        elif self.reg_method == 'contrastive':
            reg_loss = self._contrastive_regularization(features, labels)
        elif self.reg_method == 'cosine':
            reg_loss = self._cosine_regularization(features, labels)
        elif self.reg_method == 'euclidean':
            reg_loss = self._euclidean_regularization(features, labels)
        else:
            raise ValueError(f"Unknown regularization method: {self.reg_method}")

        # 2. 计算三元组损失
        triplet_loss = self._triplet_loss(features, labels)

        # 合并所有损失并应用相应权重，返回总损失
        total_loss = (self.ortho_weight * reg_loss) + \
                     (self.triplet_weight * triplet_loss)

        return total_loss

    def _enhanced_center_regularization(self, features, labels):
        """增强的类别中心正则化"""
        unique_labels = torch.unique(labels)
        if len(unique_labels) <= 1:
            return 0.0

        # 计算每个类别的中心（带权重的均值）
        centers = []
        for label in unique_labels:
            mask = (labels == label)
            class_feats = features[mask]
            # 权重与距离中心的距离成反比（降低异常值权重）
            weights = F.softmax(-torch.norm(class_feats - class_feats.mean(dim=0), dim=1), dim=0)
            weighted_center = torch.sum(class_feats * weights.unsqueeze(1), dim=0)
            centers.append(weighted_center)
        centers = torch.stack(centers)  # [C, embed_dim]

        # 1. 类内损失
        intra_loss = 0.0
        for i, label in enumerate(unique_labels):
            mask = (labels == label)
            if mask.sum() == 0:
                continue
            class_feats = features[mask]
            intra_dist = torch.norm(class_feats - centers[i].unsqueeze(0), dim=1).mean()
            intra_loss += intra_dist
        intra_loss /= len(unique_labels)

        # 2. 类间损失
        inter_loss = 0.0
        num_pairs = 0
        for i in range(len(centers)):
            for j in range(i + 1, len(centers)):
                dist = torch.norm(centers[i] - centers[j])
                # 动态margin：基于类别数量调整
                dynamic_margin = self.margin * (len(unique_labels) / (len(centers) - 1))
                inter_loss += torch.clamp(dynamic_margin - dist, min=0)
                num_pairs += 1
        inter_loss /= num_pairs if num_pairs > 0 else 1

        return intra_loss + inter_loss

    def _contrastive_regularization(self, features, labels):
        """对比损失"""
        batch_size = features.size(0)
        if batch_size <= 1:
            return 0.0

        # 计算相似度矩阵
        sim_matrix = F.cosine_similarity(features.unsqueeze(1), features.unsqueeze(0), dim=2)
        mask = 1 - torch.eye(batch_size, device=features.device)  # 排除自身

        # 同类对和异类对掩码
        same_mask = (labels.unsqueeze(0) == labels.unsqueeze(1)) * mask
        diff_mask = (labels.unsqueeze(0) != labels.unsqueeze(1)) * mask

        # 计算损失
        same_loss = (1 - sim_matrix) * same_mask
        same_loss = same_loss.sum() / (same_mask.sum() + 1e-8)

        diff_loss = torch.clamp(sim_matrix - self.margin, min=0) * diff_mask
        diff_loss = diff_loss.sum() / (diff_mask.sum() + 1e-8)

        return same_loss + diff_loss

    def _cosine_regularization(self, features, labels):
        """余弦正则化"""
        batch_size = features.size(0)
        if batch_size <= 1:
            return 0.0
        normalized_feats = F.normalize(features, p=2, dim=1)
        sim_matrix = torch.matmul(normalized_feats, normalized_feats.T)
        label_eq_matrix = (labels.unsqueeze(0) == labels.unsqueeze(1)).float()
        mask = 1 - torch.eye(batch_size, device=features.device)
        label_eq_matrix *= mask
        label_ne_matrix = (1 - label_eq_matrix) * mask
        same_label_loss = torch.mean((1 - sim_matrix) * label_eq_matrix)
        diff_label_loss = torch.mean((1 + sim_matrix) * label_ne_matrix)
        return same_label_loss + diff_label_loss

    def _euclidean_regularization(self, features, labels):
        """欧氏距离正则化"""
        batch_size = features.size(0)
        if batch_size <= 1:
            return 0.0
        norms = torch.sum(features ** 2, dim=1)
        dist_matrix = norms.unsqueeze(0) + norms.unsqueeze(1) - 2 * torch.matmul(features, features.T)
        label_eq_matrix = (labels.unsqueeze(0) == labels.unsqueeze(1)).float()
        mask = 1 - torch.eye(batch_size, device=features.device)
        label_eq_matrix *= mask
        label_ne_matrix = (1 - label_eq_matrix) * mask
        same_label_loss = torch.mean(dist_matrix * label_eq_matrix)
        diff_label_loss = torch.mean(torch.clamp(self.margin - dist_matrix, min=0) * label_ne_matrix)
        return same_label_loss + diff_label_loss

    def _triplet_loss(self, features, labels):
        """三元组损失（内部使用）"""
        batch_size = features.size(0)
        if batch_size <= 1:
            return torch.tensor(0.0, device=features.device)

        # 计算所有样本对的欧氏距离矩阵
        dist_matrix = torch.cdist(features, features, p=2)  # shape: [B, B]

        # 生成掩码
        same_label = (labels.unsqueeze(0) == labels.unsqueeze(1)).float()
        mask = 1 - torch.eye(batch_size, device=features.device)
        same_label_mask = same_label * mask
        diff_label_mask = (1 - same_label) * mask

        # 过滤无效对
        pos_dists = dist_matrix[same_label_mask.bool()]
        neg_dists = dist_matrix[diff_label_mask.bool()]
        if len(pos_dists) == 0 or len(neg_dists) == 0:
            return torch.tensor(0.0, device=features.device)

        # 计算三元组损失
        triplet_loss = torch.clamp(
            pos_dists.unsqueeze(1) - neg_dists.unsqueeze(0) + self.margin,
            min=0
        )
        return triplet_loss.mean()



# 2. 特征投影模型
# class FeatureProjectionModel(nn.Module):
#     def __init__(self, cnn_path=None, embed_dim=512):
#         super().__init__()
#
#         # 图像投影分支
#         self.img_projector = nn.Sequential(
#             nn.Linear(4096, 2048),
#             nn.ReLU(),
#             nn.Linear(2048, 1024),
#             nn.ReLU(),
#             nn.Linear(1024, embed_dim),
#             # KAN([4096, 2048, 1024, embed_dim])
#         )
#
#         # 图像特征提取器 (冻结参数)
#         self.cnn = CNN().features  # 假设CNN类已定义
#         # self.cnn = self.cnn.features  # 目标加载模块：特征提取层（无features.前缀）
#         if cnn_path is not None:
#             # 1. 加载原始权重文件（包含整个模型的参数：features.xxx 和 fc.xxx）
#             original_checkpoint = torch.load(cnn_path, weights_only=True, map_location='cpu')
#
#             # 2. 处理权重键名：只保留features子模块的参数,并去掉"features."前缀
#             processed_checkpoint = {}
#             for key, value in original_checkpoint.items():
#                 # 只保留"features."开头的键（过滤fc层等其他参数）
#                 if key.startswith("features."):
#                     # 去掉"features."前缀,得到与self.cnn匹配的键名（如"0.weight"）
#                     new_key = key[len("features."):]  # 从索引9开始截取（"features."长度为9）
#                     processed_checkpoint[new_key] = value
#
#             # 3. 用处理后的权重加载到self.cnn（此时键名完全匹配）
#             missing_keys, unexpected_keys = self.cnn.load_state_dict(
#                 processed_checkpoint, strict=False
#             )
#
#             # 4. 打印日志（验证匹配结果）
#             if len(missing_keys) != 0:
#                 print("⚠️ 模型中缺失但权重里没有的键(权重少了): ", missing_keys)
#             if len(unexpected_keys) != 0:
#                 print("⚠️ 权重里有但模型中没有的键: ", unexpected_keys)
#             else:
#                 print("✅ 特征层权重加载成功,无多余键")
#
#         for param in self.cnn.parameters():
#             param.requires_grad = False
#
#     def get_fc1_output(self, x):
#         # 1. 通过卷积层提取特征
#         with torch.no_grad():
#             conv_features = self.cnn(x)  # 形状为[batch_size, 256, 16, 16]
#
#             # 2. 扁平化特征
#             flattened = torch.flatten(conv_features, 1)  # 形状为[batch_size, 256*16*16]
#
#             # 3. 获取nn.Linear(256*16*16, 4096)层的输出
#             fc1_output = self.cnn_model.fc[0](flattened)  # 形状为[batch_size, 4096]
#
#         return fc1_output
#
#     def forward(self, img):
#         # 处理图像输入
#         img_feat = self.cnn(img)
#         img_embed = self.img_projector(img_feat)
#         return img_embed


# -------------------------- 适配多ResNet模型的FeatureProjectionModel --------------------------
class FeatureProjectionModel(nn.Module):
    def __init__(
            self,
            cnn_path: str = None,  # ResNet本地权重路径（可选）
            embed_dim: int = 512,  # 特征嵌入维度（输出维度）
            model_name: str = "resnet50"  # 新增：ResNet模型名称（默认resnet50）
    ):
        super().__init__()

        # 1. 根据模型名称创建对应ResNet（调用重构后的create_resnet）
        full_resnet = create_resnet(
            model_name=model_name,
            weight_path=cnn_path  # 传入ResNet本地权重
        )

        # 2. 截取fc层之前的特征提取结构（所有ResNet均通过children()[:-1]剔除fc层）
        self.cnn = nn.Sequential(*list(full_resnet.children())[:-1])

        # 3. 核心优化：自动获取当前ResNet的特征维度（避免写死2048，兼容resnet34/50）
        #    - resnet34：fc.in_features=512（BasicBlock，expansion=1）
        #    - resnet50：fc.in_features=2048（Bottleneck，expansion=4）
        self.resnet_feat_dim = full_resnet.fc.in_features  # 动态获取特征维度

        # 4. 冻结CNN参数（保持原逻辑）
        for param in self.cnn.parameters():
            param.requires_grad = False

        # 5. 动态创建投影层（输入维度=当前ResNet的特征维度，避免维度不匹配）
        self.img_projector = nn.Sequential(
            nn.Linear(self.resnet_feat_dim, 2048),  # 输入维度动态适配
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(1024, embed_dim),
            # KAN([self.resnet_feat_dim, 1024, 784, embed_dim]),
        )

    def forward(self, img):
        # 1. CNN输出：(batch, feat_dim, 1, 1)（avgpool结果，feat_dim=512/2048）
        # 2. 展平：(batch, feat_dim)（动态适配特征维度）
        img_feat = self.cnn(img).flatten(start_dim=1)
        # 3. 特征投影：feat_dim → embed_dim（维度完全匹配）
        img_embed = self.img_projector(img_feat)
        return img_embed

class LSELoss(nn.Module):
    def __init__(self, hsa_matrix):
        """
        LSE损失函数实现（支持普通数据自动转为Tensor）
        Args:
            hsa_matrix (list / np.ndarray / torch.Tensor): HSA矩阵
        """
        super().__init__()
        # 核心：自动将任意兼容输入转为Tensor,并指定 dtype
        hsa_tensor = torch.as_tensor(hsa_matrix, dtype=torch.float32)
        # 注册为buffer,保证与模型参数设备（CPU/GPU）一致,且不参与梯度更新
        self.register_buffer('hsa', hsa_tensor)

    def forward(self, embedded_features, targets):
        """
        前向计算（逻辑完全不变）
        Args:
            embedded_features (Tensor): 嵌入特征 [batch_size, feature_dim]
            targets (LongTensor): 类别标签 [batch_size]（需为长整型,对应类别索引）
        Returns:
            Tensor: 平均最小二乘损失值
        """
        # 选择目标类别对应的HSA向量（自动匹配设备）
        selected_hsa = self.hsa[targets]  # 形状：[batch_size, feature_dim]

        # 计算批量平均最小二乘误差
        loss = torch.sum((embedded_features - selected_hsa) ** 2) / targets.size(0)

        return loss


class EuclideanDistanceLoss(nn.Module):  # 类名修改：明确表示「欧几里得距离损失」
    def __init__(self, hsa_matrix):
        """
        欧几里得距离损失实现（支持普通数据自动转为Tensor）
        功能：计算嵌入特征与目标类别HSA向量的欧几里得距离,返回批量平均值
        Args:
            hsa_matrix (list / np.ndarray / torch.Tensor): HSA矩阵
                输入格式支持：列表、NumPy数组、PyTorch Tensor
                形状要求：[num_classes, feature_dim]（类别数 × 特征维度）
        """
        super().__init__()
        # 自动将输入转为float32 Tensor（特征计算常用类型）
        hsa_tensor = torch.as_tensor(hsa_matrix, dtype=torch.float32)
        # 注册为buffer：与模型设备（CPU/GPU）同步,且不参与梯度更新
        self.register_buffer('hsa', hsa_tensor)

    def forward(self, embedded_features, targets):
        """
        前向计算：批量欧几里得距离的平均值
        Args:
            embedded_features (torch.Tensor): 嵌入特征
                形状：[batch_size, feature_dim]（样本数 × 特征维度）
            targets (torch.LongTensor): 类别标签
                形状：[batch_size]（需为长整型,对应HSA矩阵的类别索引）
        Returns:
            torch.Tensor: 批量平均欧几里得距离（标量Tensor）
        """
        # 1. 选择每个样本目标类别的HSA向量（自动匹配设备）
        selected_hsa = self.hsa[targets]  # 形状：[batch_size, feature_dim]

        # 2. 计算每个样本的欧几里得距离（L2范数）
        # dim=1：对每个样本的「特征维度」求范数,得到单个样本的距离
        sample_distances = torch.norm(embedded_features - selected_hsa, dim=1)

        # 3. 计算批量平均距离（损失值）
        avg_distance = torch.mean(sample_distances)

        return avg_distance


class DistanceLoss(nn.Module):
    """
    多模式距离损失类：支持欧氏距离、余弦损失和类别中心正则化
    通过reg_method参数切换损失计算方式
    """

    def __init__(self, hsa_matrix, reg_method='euclidean', center_weight=0.1):
        """
        初始化损失函数
        Args:
            hsa_matrix (list / np.ndarray / torch.Tensor): 类别特征矩阵
                形状：[num_classes, feature_dim]
            reg_method (str): 损失计算方式
                可选值：'euclidean'（欧氏距离）、'cosine'（余弦损失）、'euclidean_center'（欧氏+中心正则）、
                        'cosine_center'（余弦+中心正则）
            center_weight (float): 类别中心正则化权重（仅在含center的模式下生效）
        """
        super().__init__()
        # 处理HSA矩阵（自动转为Tensor并注册为非参数缓冲区）
        hsa_tensor = torch.as_tensor(hsa_matrix, dtype=torch.float32)
        self.register_buffer('hsa', hsa_tensor)
        self.num_classes = hsa_tensor.shape[0]
        self.feature_dim = hsa_tensor.shape[1]

        # 配置参数
        self.reg_method = reg_method
        self.center_weight = center_weight

        # 初始化可学习的类别中心（用于正则化）
        if 'center' in reg_method:
            self.class_centers = nn.Parameter(hsa_tensor.clone())  # 以HSA矩阵为初始值
        else:
            self.class_centers = None

    def forward(self, embedded_features, targets):
        """
        前向计算损失
        Args:
            embedded_features (torch.Tensor): 嵌入特征 [batch_size, feature_dim]
            targets (torch.LongTensor): 类别标签 [batch_size]
        Returns:
            torch.Tensor: 计算得到的损失值（标量）
        """
        # 获取目标类别对应的HSA特征
        target_hsa = self.hsa[targets]  # [batch_size, feature_dim]

        # 基础损失计算
        if self.reg_method in ['euclidean', 'euclidean_center']:
            # 欧氏距离损失：||f - hsa||
            base_loss = torch.mean(torch.norm(embedded_features - target_hsa, dim=1))
        elif self.reg_method in ['cosine', 'cosine_center']:
            # 余弦损失：1 - cos(f, hsa)（余弦相似度越大，损失越小）
            cos_sim = F.cosine_similarity(embedded_features, target_hsa, dim=1)
            base_loss = torch.mean(1 - cos_sim)
        else:
            raise ValueError(f"不支持的损失模式: {self.reg_method}")

        # 类别中心正则化（仅在指定模式下生效）
        reg_loss = 0.0
        if 'center' in self.reg_method and self.class_centers is not None:
            # 1. 计算当前批次中每个类别的特征中心
            batch_centers = []
            batch_classes = torch.unique(targets)
            for cls in batch_classes:
                mask = (targets == cls)
                cls_features = embedded_features[mask]
                batch_center = torch.mean(cls_features, dim=0)  # 批次内类别中心
                batch_centers.append(batch_center)

            # 2. 计算批次中心与模型学习的类别中心之间的距离
            if batch_centers:
                batch_centers = torch.stack(batch_centers)  # [num_unique_classes, feature_dim]
                model_centers = self.class_centers[batch_classes]  # [num_unique_classes, feature_dim]

                if self.reg_method == 'euclidean_center':
                    reg_loss = torch.mean(torch.norm(batch_centers - model_centers, dim=1))
                else:  # cosine_center
                    cos_sim = F.cosine_similarity(batch_centers, model_centers, dim=1)
                    reg_loss = torch.mean(1 - cos_sim)

        # 总损失 = 基础损失 + 正则化损失*权重
        total_loss = base_loss + self.center_weight * reg_loss
        return total_loss

class ProjectionModel(nn.Module):
    def __init__(self, class_dims, attribute_dim=64, disent_path=None, num_class=10):
        super().__init__()
        self.disentangled_model = DisentangledModel(class_dims, attribute_dim)
        if disent_path is not None:
            self.disentangled_model.load_state_dict(torch.load(disent_path, weights_only=True, map_location='cpu'))
        self.projector = nn.Sequential(
            nn.Linear(attribute_dim*2, 512),
            nn.ReLU(),
            nn.Linear(512, 1024),
            nn.ReLU(),
            nn.Linear(1024, 2048),
            nn.ReLU(),
            nn.Linear(2048, num_class),
        )

    def forward(self, img):
        _, branch_outputs = self.disentangled_model(img)
        last_two_branches = branch_outputs[-2:]  # 取最后两个分支
        # 拼接最后两个分支的特征 (在特征维度拼接)
        merged_features = torch.cat(last_two_branches, dim=1)  # 形状: [B, attribute_dim*2]
        output = self.projector(merged_features)
        return output





if __name__ == '__main__':
    model = ProjectionModel([4,4,4])
    x = torch.randn(1, 3, 64, 64)
    y = model(x)
    print(y)
    # w = torch.load(r'D:\Code\2-ZSL\1-output\论文实验结果\TaskA_CWRU_06\exp-1\checkpoints\feature_projection.pth',
    #                weights_only=True, map_location='cpu')
    # missing_keys, unexpected_keys = model.load_state_dict(w, strict=False)
    # if len(missing_keys) != 0:
    #     print("⚠️ 模型中缺失但权重里没有的键（需检查模型结构）: ", missing_keys)
    # if len(unexpected_keys) != 0:
    #     print("⚠️ 权重里有但模型中没有的键（已过滤）: ", unexpected_keys)
    # else:
    #     print("✅ 特征层权重加载成功,无多余键")
    # data = torch.randn(1, 3, 64, 64)
    # y = model(data)
    # print(y.size())
