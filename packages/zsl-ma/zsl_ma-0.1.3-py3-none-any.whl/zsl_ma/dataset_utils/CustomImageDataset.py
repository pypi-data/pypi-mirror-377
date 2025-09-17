import os
import random
import re
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from zsl_ma.dataset_utils.FactorLabelMapper import FactorLabelMapper, load_class_list


class ImageClassificationDataset(Dataset):
    """
    自定义数据集类
    """

    def __init__(self, root_dir, transform=None, train_class=None, mode='train', ignore_factors=None,
                 factor_index_map_path=None):
        """
        初始化数据集

        参数:
            root_dir (str): 数据集根目录路径
            transform (callable, optional): 应用于图像的变换/增强
            target_transform (callable, optional): 应用于标签的变换
            mode (str): 数据集模式，如 'train', 'val', 'test'
        """
        self.root_dir = Path(root_dir)
        self.mode = mode
        self.transform = transform

        # 构建数据路径
        self.data_dir = self.root_dir / mode

        # 确保目录存在
        if not self.data_dir.exists():
            raise ValueError(f"目录不存在: {self.data_dir}")

        # 2. 初始化训练类别映射器
        self.mapper = FactorLabelMapper(
            data_dir=self.data_dir,  # 当train_class不存在时，从当前模式目录提取训练类别
            class_list_path=train_class,
            ignore_factors=ignore_factors,
            factor_index_map_path=factor_index_map_path
        )
        self.train_classes = self.mapper.raw_classes  # 训练使用的类别
        self.classes = self.mapper.classes  # 实际预测的所有类别
        self.class_to_idx = self.mapper.class_to_idx  # 基于预测类别构建的映射

        # 3. 验证：训练类别必须完全包含在预测类别中
        # for cls in self.train_classes:
        #     if cls not in self.classes:
        #         raise ValueError(f"训练类别 '{cls}' 不在预测类别列表中，请确保预测类别包含所有训练类别")

        # # 获取所有类别文件夹
        # self.maper = FactorLabelMapper(self.data_dir, train_class)
        # self.classes = self.maper.classes
        # if not self.classes:
        #     raise ValueError(f"在 {self.data_dir} 中未找到任何类别文件夹")
        #
        # # 创建类别到索引的映射
        # self.class_to_idx = self.maper.class_to_idx

        # 收集所有图像路径和对应的标签
        self.image_paths = []
        self.labels = []

        for class_name in self.train_classes:
            class_dir = self.data_dir / class_name
            class_idx = self.class_to_idx[class_name]

            # 获取此类别的所有图像文件
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            for ext in image_extensions:
                for img_path in class_dir.glob(f'*{ext}'):
                    self.image_paths.append(img_path)
                    self.labels.append(class_idx)

        if not self.image_paths:
            raise ValueError(f"在 {self.data_dir} 中未找到任何图像文件")

    def __len__(self):
        """返回数据集中的样本数量"""
        return len(self.image_paths)

    def __getitem__(self, idx):
        """
        获取单个样本

        参数:
            idx (int): 样本索引

        返回:
            tuple: (图像, 标签)
        """
        img_path = self.image_paths[idx]
        label = self.labels[idx]

        # 加载图像
        image = Image.open(img_path).convert('RGB')  # 确保图像是RGB格式

        # 应用变换
        if self.transform:
            image = self.transform(image)

        return image, label

    def get_class_distribution(self):
        """返回每个类别的样本数量"""
        class_counts = {cls: 0 for cls in self.classes}
        for label in self.labels:
            class_name = self.classes[label]
            class_counts[class_name] += 1
        return class_counts

    def get_class_num(self):
        return len(self.classes)


class FeatureDecouplingDataset(Dataset):
    def __init__(self, root_dir, transform=None, train_class=None, mode='train', factor_index_map_path=None, ignore_factors=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.data_dir = self.root_dir / mode

        self.maper = FactorLabelMapper(self.data_dir, train_class,
                                       factor_index_map_path=factor_index_map_path, ignore_factors=ignore_factors)
        self.train_classes = self.maper.raw_classes

        self.classes = self.maper.classes

        # 创建类别到索引的映射
        self.class_to_idx = self.maper.class_to_idx

        # 收集所有图像路径和对应的标签
        self.image_paths = []
        self.labels = []
        self.indices = []

        for class_name in self.train_classes:
            class_dir = self.data_dir / class_name
            class_idx = self.class_to_idx[class_name]

            # 获取此类别的所有图像文件
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            for ext in image_extensions:
                for img_path in class_dir.glob(f'*{ext}'):
                    self.image_paths.append(img_path)
                    self.labels.append(class_idx)
                    self.indices.append(
                        self.maper.get_indices_from_factors(self.maper.get_factors_from_class(class_name)))

        if not self.image_paths:
            raise ValueError(f"在 {self.data_dir} 中未找到任何图像文件")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]

        # 加载图像
        image = Image.open(img_path).convert('RGB')  # 确保图像是RGB格式

        # 应用变换
        if self.transform:
            image = self.transform(image)
        indices = self.indices[idx]

        return image, indices, label


class EmbeddingDataset(Dataset):
    """用于嵌入学习任务的数据集类"""

    def __init__(self, root_dir, semantic_path, train_class, factor_index_map_path,
                 ignore_factors=["工况"],
                 transform=None,
                 mode='train',
                 neg_ratio=1):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.data_dir = self.root_dir / mode
        self.neg_ratio = neg_ratio
        self.semantic_path = semantic_path


        self.maper = FactorLabelMapper(self.data_dir, train_class, factor_index_map_path, ignore_factors=ignore_factors)
        self.train_classes = self.maper.raw_classes
        self.classes = self.maper.classes
        self.class_to_idx = self.maper.class_to_idx

        # self.data_class = load_class_list(train_class)
        # self.classes = load_class_list(classes)
        # self.class_to_idx: Dict[str, int] = {cls: idx for idx, cls in enumerate(self.classes)}  # 类别→索引
        self.idx_to_class: Dict[int, str] = {idx: cls for cls, idx in self.class_to_idx.items()}  # 索引→类别（反向映射）

        # 收集所有图像路径和对应的标签
        self.image_info = []
        # self.labels = []
        for class_name in self.train_classes:
            class_dir = self.data_dir / class_name
            factors = self.maper.get_factors_from_class(class_name)
            class_id = self.maper.get_class_from_factors(factors)

            # 获取此类别的所有图像文件
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            for ext in image_extensions:
                for img_path in class_dir.glob(f'*{ext}'):
                    self.image_info.append((img_path, class_id))
                    # self.labels.append(class_idx)

        if not self.image_info:
            raise ValueError(f"在 {self.data_dir} 中未找到任何图像文件")

        self.semantic_attributes = []
        for cls_name in self.classes:
            npy_path = os.path.join(self.semantic_path, f"{cls_name}.npy")
            self.semantic_attributes.append(np.load(npy_path, allow_pickle=True))

    def __len__(self):
        # 总样本数 = 图片数量 × (1个正样本 + neg_ratio个负样本)
        return len(self.image_info) * (1 + self.neg_ratio)

    def __getitem__(self, idx):
        # 1. 确定当前样本对应的图片和正负标签
        img_idx = idx // (1 + self.neg_ratio)  # 原始图片索引
        is_positive = (idx % (1 + self.neg_ratio)) == 0  # 第0个为正样本，其余为负样本

        img_path, class_id = self.image_info[img_idx]
        img = Image.open(img_path).convert("RGB")
        img = self.transform(img)

        if is_positive:
            sem_idx = self.class_to_idx[class_id]
            x2 = torch.tensor(self.semantic_attributes[sem_idx], dtype=torch.float32)
            target = torch.tensor(1.0, dtype=torch.float32)
        else:
            other_classes = [cls for cls in self.classes if cls != class_id]
            neg_class = random.choice(other_classes)
            sem_idx = self.class_to_idx[neg_class]
            x2 = torch.tensor(self.semantic_attributes[sem_idx], dtype=torch.float32)  # (M,)
            target = torch.tensor(-1.0, dtype=torch.float32)

        return img, x2, target



# class CustomNpyDataset(Dataset):
#     def __init__(self, location_path, size_path):
#         """
#         Args:
#             location_path (string): 故障位置数据文件夹路径
#             size_path (string): 故障尺寸数据文件夹路径
#         """
#         self.location_path = location_path
#         self.size_path = size_path
#
#         # 加载所有数据文件并提取维度信息
#         self.location_files = {}
#         self.size_files = {}
#         self.dim = None
#         self.N = None
#         self.M = None
#
#         # 加载故障位置数据
#         for file_name in os.listdir(location_path):
#             if file_name.endswith('.npy'):
#                 key = file_name.split('.')[0]
#                 file_path = os.path.join(location_path, file_name)
#                 data = np.load(file_path)
#                 self.location_files[key] = data
#
#                 # 确定维度信息
#                 if key != 'No':
#                     if self.N is None:
#                         self.N = data.shape[0]
#                     else:
#                         assert data.shape[0] == self.N, f"{file_name} 的样本数量与其他位置文件不一致"
#
#                     if self.dim is None:
#                         self.dim = data.shape[1]
#                     else:
#                         assert data.shape[1] == self.dim, f"{file_name} 的特征维度与其他文件不一致"
#                 else:
#                     if self.M is None:
#                         self.M = data.shape[0]
#                     else:
#                         assert data.shape[0] == self.M, f"{file_name} 的样本数量与其他位置文件不一致"
#
#                     if self.dim is None:
#                         self.dim = data.shape[1]
#                     else:
#                         assert data.shape[1] == self.dim, f"{file_name} 的特征维度与其他文件不一致"
#
#         # 加载故障尺寸数据
#         for file_name in os.listdir(size_path):
#             if file_name.endswith('.npy'):
#                 # 提取尺寸名称（去除非数字字符）
#                 size_name = re.sub(r'[^0-9]', '', file_name.split('.')[0])
#                 file_path = os.path.join(size_path, file_name)
#                 data = np.load(file_path)
#                 self.size_files[size_name] = data
#
#                 # 验证尺寸数据的维度
#                 if size_name != '0':
#                     assert data.shape[0] == self.N, f"{file_name} 的样本数量与位置文件不一致"
#                 else:
#                     assert data.shape[0] == self.M, f"{file_name} 的样本数量与No位置文件不一致"
#
#                 assert data.shape[1] == self.dim, f"{file_name} 的特征维度与其他文件不一致"
#
#         # 确保N是3的倍数
#         assert self.N % 3 == 0, f"N ({self.N}) 必须是3的倍数"
#
#         # 获取所有尺寸（去除0）
#         self.sizes = [size for size in self.size_files.keys() if size != '0']
#
#         # 获取所有位置（去除No）
#         self.locations = [loc for loc in self.location_files.keys() if loc != 'No']
#
#         # 计算每个组合的样本数
#         self.chunk_size = self.N // len(self.sizes)
#
#         # 初始化样本和标签列表（将在每个epoch重置）
#         self.samples = []
#         self.labels = []
#         self.label_indices = []
#
#         # 创建标签映射
#         self.unique_labels = []
#         for loc in self.locations:
#             for size in self.sizes:
#                 self.unique_labels.append(f"{loc}-{size}")
#         if 'No' in self.location_files and '0' in self.size_files:
#             self.unique_labels.append("No-0")
#
#         self.label_to_idx = {label: idx for idx, label in enumerate(self.unique_labels)}
#
#         # 设置随机种子
#         self.seed = 0
#         random.seed(self.seed)
#
#         # 准备第一个epoch的数据
#         self._prepare_epoch_data()
#
#     def _prepare_epoch_data(self):
#         """为当前epoch准备数据"""
#         # 清空样本和标签列表
#         self.samples = []
#         self.labels = []
#
#         # 为每个尺寸创建随机索引
#         size_indices = {}
#         for size in self.sizes:
#             if size in self.size_files:
#                 indices = list(range(self.N))
#                 random.shuffle(indices)
#                 size_indices[size] = {}
#
#                 for i, loc in enumerate(self.locations):
#                     start_idx = i * self.chunk_size
#                     end_idx = (i + 1) * self.chunk_size
#                     size_indices[size][loc] = indices[start_idx:end_idx]
#
#         # 为每个位置创建随机索引
#         location_indices = {}
#         for loc in self.locations:
#             if loc in self.location_files:
#                 indices = list(range(self.N))
#                 random.shuffle(indices)
#                 location_indices[loc] = {}
#
#                 for i, size in enumerate(self.sizes):
#                     start_idx = i * self.chunk_size
#                     end_idx = (i + 1) * self.chunk_size
#                     location_indices[loc][size] = indices[start_idx:end_idx]
#
#         # 为No-0类别创建随机索引
#         no_indices = list(range(self.M))
#         zero_indices = list(range(self.M))
#         random.shuffle(no_indices)
#         random.shuffle(zero_indices)
#
#         # 添加位置-尺寸组合样本
#         for loc in self.locations:
#             for size in self.sizes:
#                 if loc in self.location_files and size in self.size_files:
#                     label = f"{loc}-{size}"
#
#                     for i in range(self.chunk_size):
#                         # 获取对应索引
#                         loc_idx = location_indices[loc][size][i]
#                         size_idx = size_indices[size][loc][i]
#
#                         # 拼接数据
#                         loc_data = self.location_files[loc][loc_idx]
#                         size_data = self.size_files[size][size_idx]
#                         combined_data = np.concatenate([loc_data, size_data])
#
#                         self.samples.append(combined_data)
#                         self.labels.append(label)
#
#         # 添加No-0样本
#         if 'No' in self.location_files and '0' in self.size_files:
#             for i in range(self.M):
#                 no_idx = no_indices[i]
#                 zero_idx = zero_indices[i]
#
#                 no_data = self.location_files['No'][no_idx]
#                 zero_data = self.size_files['0'][zero_idx]
#                 combined_data = np.concatenate([no_data, zero_data])
#
#                 self.samples.append(combined_data)
#                 self.labels.append("No-0")
#
#         # 转换为numpy数组
#         self.samples = np.array(self.samples)
#         self.labels = np.array(self.labels)
#
#
#         # 将标签映射为整数
#         self.label_indices = np.array([self.label_to_idx[label] for label in self.labels])
#
#         # 增加随机种子，以便下一个epoch使用不同的随机组合
#         self.seed += 1
#         random.seed(self.seed)
#
#     def set_epoch(self, epoch):
#         """设置当前epoch，准备新的数据组合"""
#         self.seed = epoch
#         random.seed(self.seed)
#         self._prepare_epoch_data()
#
#     def __len__(self):
#         return len(self.samples)
#
#     def __getitem__(self, idx):
#         sample = torch.tensor(self.samples[idx], dtype=torch.float32)
#         label = torch.tensor(self.label_indices[idx], dtype=torch.long)
#
#         return sample, label
#
#     def get_label_mapping(self):
#         return self.label_to_idx
#
#     def get_data_info(self):
#         """返回数据集的信息"""
#         return {
#             'N': self.N,
#             'M': self.M,
#             'dim': self.dim,
#             'total_samples': len(self.samples),
#             'label_distribution': {label: np.sum(self.labels == label) for label in self.unique_labels},
#             'location_files': list(self.location_files.keys()),
#             'size_files': list(self.size_files.keys())
#         }


class CustomNpyDataset(Dataset):
    def __init__(self, location_path, size_path):
        """
        Args:
            location_path (string): 故障位置数据文件夹路径
            size_path (string): 故障尺寸数据文件夹路径
        """
        self.location_path = location_path
        self.size_path = size_path

        # 加载所有数据文件并提取维度信息
        self.location_files = {}  # 存储位置数据（key: 位置名，如'B'/'IR'/'No'）
        self.size_files = {}  # 存储尺寸数据（key: 尺寸名，如'007'/'014'/'0'）
        self.dim = None  # 特征维度（所有数据统一）
        self.N = None  # 正常位置/尺寸数据的样本数（非No/非0）
        self.M = None  # No位置/0尺寸数据的样本数

        # -------------------------- 1. 加载故障位置数据（区分正常位置与No） --------------------------
        for file_name in os.listdir(location_path):
            if file_name.endswith('.npy'):
                key = file_name.split('.')[0]  # 位置名（如'B'/'IR'/'No'）
                file_path = os.path.join(location_path, file_name)
                data = np.load(file_path)
                self.location_files[key] = data

                # 验证并记录维度信息
                if key != 'No':  # 正常位置数据（如'B'/'IR'）
                    if self.N is None:
                        self.N = data.shape[0]
                    else:
                        assert data.shape[0] == self.N, f"{file_name} 样本数({data.shape[0]})≠正常样本数({self.N})"

                    if self.dim is None:
                        self.dim = data.shape[1]
                    else:
                        assert data.shape[1] == self.dim, f"{file_name} 特征维度({data.shape[1]})≠统一维度({self.dim})"
                else:  # No位置数据
                    if self.M is None:
                        self.M = data.shape[0]
                    else:
                        assert data.shape[0] == self.M, f"{file_name} 样本数({data.shape[0]})≠No样本数({self.M})"

                    if self.dim is None:
                        self.dim = data.shape[1]
                    else:
                        assert data.shape[1] == self.dim, f"{file_name} 特征维度({data.shape[1]})≠统一维度({self.dim})"

        # -------------------------- 2. 加载故障尺寸数据（区分正常尺寸与0） --------------------------
        for file_name in os.listdir(size_path):
            if file_name.endswith('.npy'):
                # 提取尺寸名（去除非数字字符，如'IR-007'→'007'，'0'→'0'）
                size_name = re.sub(r'[^0-9]', '', file_name.split('.')[0])
                file_path = os.path.join(size_path, file_name)
                data = np.load(file_path)
                self.size_files[size_name] = data

                # 验证样本数与维度
                if size_name != '0':  # 正常尺寸数据（如'007'/'014'）
                    assert data.shape[0] == self.N, f"{file_name} 样本数({data.shape[0]})≠正常样本数({self.N})"
                else:  # 0尺寸数据
                    assert data.shape[0] == self.M, f"{file_name} 样本数({data.shape[0]})≠0样本数({self.M})"

                assert data.shape[1] == self.dim, f"{file_name} 特征维度({data.shape[1]})≠统一维度({self.dim})"

        # -------------------------- 3. 初始化核心变量（区分正常组合与特殊组合） --------------------------
        # 正常组合：非No位置 + 非0尺寸（需全搭配）
        self.normal_locations = [loc for loc in self.location_files.keys() if loc != 'No']  # 正常位置列表
        self.normal_sizes = [sz for sz in self.size_files.keys() if sz != '0']  # 正常尺寸列表
        self.L = len(self.normal_locations)  # 正常位置数量
        self.S = len(self.normal_sizes)  # 正常尺寸数量

        # 特殊组合：No位置 + 0尺寸（仅一种固定搭配）
        self.has_no_zero = 'No' in self.location_files and '0' in self.size_files

        # 验证正常样本数合理性（原逻辑保留）
        if self.L > 0 and self.S > 0:
            assert self.N >= max(self.L, self.S), f"正常样本数({self.N})需≥位置数({self.L})/尺寸数({self.S})"

        # -------------------------- 4. 标签映射与初始化 --------------------------
        # 生成所有唯一标签（正常组合 + 特殊组合）
        self.unique_labels = []
        # 正常组合：每个位置×每个尺寸
        for loc in self.normal_locations:
            for sz in self.normal_sizes:
                self.unique_labels.append(f"{loc}-{sz}")
        # 特殊组合：No-0
        if self.has_no_zero:
            self.unique_labels.append("No-0")

        # 标签→索引映射
        self.label_to_idx = {label: idx for idx, label in enumerate(self.unique_labels)}

        # 随机种子（控制每次epoch的打乱/舍弃逻辑）
        self.seed = 0
        random.seed(self.seed)

        # 准备第一个epoch数据
        self._prepare_epoch_data()

    def _prepare_epoch_data(self):
        """
        核心逻辑：为当前epoch准备数据
        满足需求：
        1. 正常组合（loc-sz）全搭配；
        2. 每种组合样本数相同；
        3. 单epoch内loc/sz数据仅用一次；
        4. 多余样本随机舍弃，每次epoch舍弃不同。
        """
        self.samples = []  # 存储拼接后的样本（shape: [total, 2*dim]）
        self.labels = []  # 存储标签（如'B-007'/'No-0'）

        # -------------------------- 1. 处理正常组合（loc≠No，sz≠0） --------------------------
        if self.L > 0 and self.S > 0:
            # 步骤1：计算统一组合样本数K（关键！确保无重复+数量一致）
            # K = 最小可行值：每个loc能分给S个sz（K*S ≤ N），每个sz能分给L个loc（K*L ≤ N）
            K = min(self.N // self.S, self.N // self.L)
            if K == 0:
                raise ValueError(f"正常位置数({self.L})/尺寸数({self.S})过大，无法分配样本（N={self.N}）")

            # 步骤2：为每个正常loc生成「无重复随机索引」，取前K*S个（分给S个sz，每个K个）
            # 多余样本（N-K*S个）随机舍弃（因每次打乱不同，舍弃部分不同）
            loc_usable_indices = {}
            for loc in self.normal_locations:
                # 生成无重复的随机索引（全量N个样本打乱）
                full_shuffled_idx = random.sample(range(self.N), self.N)
                # 取前K*S个可用索引（确保能平均分给S个sz）
                loc_usable_indices[loc] = full_shuffled_idx[:K * self.S]

            # 步骤3：为每个正常sz生成「无重复随机索引」，取前K*L个（分给L个loc，每个K个）
            sz_usable_indices = {}
            for sz in self.normal_sizes:
                full_shuffled_idx = random.sample(range(self.N), self.N)
                sz_usable_indices[sz] = full_shuffled_idx[:K * self.L]

            # 步骤4：拆分索引→每个loc-sz组合分配K个不重复索引
            # 拆分loc索引：每个loc的K*S个索引→分成S份，每份K个（对应每个sz）
            loc_split_idx = {}
            for loc in self.normal_locations:
                idx_list = loc_usable_indices[loc]
                # 平均拆分（S份，每份K个）
                split = [idx_list[i * K: (i + 1) * K] for i in range(self.S)]
                # 映射到对应sz（与self.normal_sizes顺序一致）
                loc_split_idx[loc] = dict(zip(self.normal_sizes, split))

            # 拆分sz索引：每个sz的K*L个索引→分成L份，每份K个（对应每个loc）
            sz_split_idx = {}
            for sz in self.normal_sizes:
                idx_list = sz_usable_indices[sz]
                split = [idx_list[i * K: (i + 1) * K] for i in range(self.L)]
                # 映射到对应loc（与self.normal_locations顺序一致）
                sz_split_idx[sz] = dict(zip(self.normal_locations, split))

            # 步骤5：拼接每个loc-sz组合的样本（确保无重复）
            for loc in self.normal_locations:
                for sz in self.normal_sizes:
                    label = f"{loc}-{sz}"
                    # 获取当前组合的loc/sz索引（各K个，无重复）
                    loc_idx_list = loc_split_idx[loc][sz]
                    sz_idx_list = sz_split_idx[sz][loc]

                    # 逐个拼接数据（loc特征 + sz特征，维度2*dim）
                    for loc_idx, sz_idx in zip(loc_idx_list, sz_idx_list):
                        loc_data = self.location_files[loc][loc_idx]
                        sz_data = self.size_files[sz][sz_idx]
                        combined_data = np.concatenate([loc_data, sz_data])
                        self.samples.append(combined_data)
                        self.labels.append(label)

        # -------------------------- 2. 处理特殊组合（No-0） --------------------------
        if self.has_no_zero:
            # 生成No和0的无重复随机索引（单epoch内仅用一次）
            no_shuffled_idx = random.sample(range(self.M), self.M)
            zero_shuffled_idx = random.sample(range(self.M), self.M)

            # 拼接所有No-0样本（数量=M，无重复）
            for no_idx, zero_idx in zip(no_shuffled_idx, zero_shuffled_idx):
                no_data = self.location_files['No'][no_idx]
                zero_data = self.size_files['0'][zero_idx]
                combined_data = np.concatenate([no_data, zero_data])
                self.samples.append(combined_data)
                self.labels.append("No-0")

        # -------------------------- 3. 格式转换与标签索引映射 --------------------------
        self.samples = np.array(self.samples, dtype=np.float32)  # 转为numpy数组（节省内存）
        self.labels = np.array(self.labels)
        # 标签→整数索引（适配模型训练）
        self.label_indices = np.array([self.label_to_idx[label] for label in self.labels], dtype=np.int64)

        # 更新种子（下一个epoch用不同打乱/舍弃逻辑）
        self.seed += 1
        random.seed(self.seed)

    def set_epoch(self, epoch):
        """设置当前epoch，触发新的数据组合（确保不同epoch的舍弃/打乱不同）"""
        self.seed = epoch  # 用epoch作为种子，保证可复现
        random.seed(self.seed)
        self._prepare_epoch_data()

    def __len__(self):
        """返回当前epoch的总样本数"""
        return len(self.samples)

    def __getitem__(self, idx):
        """按索引获取样本与标签（转为PyTorch Tensor）"""
        sample = torch.tensor(self.samples[idx], dtype=torch.float32)
        label = torch.tensor(self.label_indices[idx], dtype=torch.long)
        return sample, label

    def get_label_mapping(self):
        """返回标签→索引的映射字典（用于后续结果解析）"""
        return self.label_to_idx.copy()

    def get_data_info(self):
        """返回数据集关键信息（用于调试/日志）"""
        label_dist = {label: np.sum(self.labels == label) for label in self.unique_labels}
        return {
            '正常位置数': self.L,
            '正常尺寸数': self.S,
            '正常组合数': self.L * self.S,
            '正常组合样本数/每个': min(self.N // self.S, self.N // self.L) if (self.L > 0 and self.S > 0) else 0,
            'No-0样本数': self.M if self.has_no_zero else 0,
            '特征维度（单部分）': self.dim,
            '拼接后特征维度': 2 * self.dim,
            '当前epoch总样本数': len(self.samples),
            '标签分布': label_dist,
            '位置数据列表': list(self.location_files.keys()),
            '尺寸数据列表': list(self.size_files.keys())
        }




if __name__ == '__main__':
    # print()
    # data = EmbeddingDataset(r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu',
    #                         r'D:\Code\2-ZSL\1-output\特征解耦结果\exp\attributes\semantic_attribute',
    #                         train_class=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\seen_classes.txt',
    #                         transform=transforms.ToTensor(),
    #                         mode='val',
    #                         factor_index_map_path=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\factor_index_map.txt'
    #                         )
    # data = FeatureDecouplingDataset(r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu',
    #                         train_class=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\seen_classes.txt',
    #                         transform=transforms.ToTensor(),
    #                         mode='val',
    #                         factor_index_map_path=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\factor_index_map.txt'
    #                         )
    # data = ImageClassificationDataset(r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu',
    #                         train_class=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\custom_index_classes.txt',
    #                         transform=transforms.ToTensor(),
    #                         mode='val',
    #                         )
    data = CustomNpyDataset('/data/coding/output/TaskA_CWRU_06/exp-1/attributes/train_semantic_embed/val/Fault Location',
                            '/data/coding/output/TaskA_CWRU_06/exp-1/attributes/train_semantic_embed/val/Fault Size')
    data_info = data.get_data_info()
    print("数据集信息：")
    for k, v in data_info.items():
        print(f"  {k}: {v}")
    # dataloader = DataLoader(data, batch_size=10, shuffle=False)
    # for epoch in range(100):
    #     for sample, label in dataloader:
    #         print(label )
