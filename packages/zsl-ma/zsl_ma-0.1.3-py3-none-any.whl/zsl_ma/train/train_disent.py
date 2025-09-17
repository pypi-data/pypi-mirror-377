import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Union

import numpy as np
import torch
from torch.nn import CrossEntropyLoss
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchvision import transforms

from zsl_ma.dataset_utils.CustomImageDataset import FeatureDecouplingDataset
from zsl_ma.models.DisentangledModel import DisentangledModel
from zsl_ma.tools.predict_untils import disent_predict
from zsl_ma.tools.tool import get_device, setup_save_dirs, create_csv, calculate_metric, append_metrics_to_csv, \
    save_class_mean_features, concat_fault_features, extract_class_features, setup_logger
from zsl_ma.tools.train_val_until import train_disent_one_epoch, val_disent_one_epoch
import warnings

warnings.filterwarnings("ignore")
logger = logging.getLogger('zsl_train')

def train_disent(configs, run=None):
    device = configs.device
    transform = configs.transform
    save_dir = configs.save_dir
    results_file = os.path.join(save_dir, 'disent_metrics.csv')
    metrics = ['train_loss', 'val_loss', 'accuracy', 'precision', 'recall', 'f1-score', 'lr']
    create_csv(metrics, results_file)

    train_dataset = FeatureDecouplingDataset(configs.data_dir, transform=transform, train_class=configs.train_class,
                                             factor_index_map_path=configs.factor_index_map_path,
                                             ignore_factors=configs.ignore_factors)
    val_dataset = FeatureDecouplingDataset(configs.data_dir, transform=transform, train_class=configs.train_class,
                                           mode='val', factor_index_map_path=configs.factor_index_map_path,
                                           ignore_factors=configs.ignore_factors)
    train_loader = DataLoader(train_dataset, batch_size=configs.batch_size, shuffle=True,
                              num_workers=configs.num_workers)
    val_loader = DataLoader(val_dataset, batch_size=configs.batch_size, shuffle=False, num_workers=configs.num_workers)

    classes = train_dataset.classes

    model = DisentangledModel(class_dims=configs.class_dims, attribute_dim=configs.attribute_dim,
                              ortho_weight=configs.ortho_weight).to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=configs.lr)
    lr_scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.1, patience=5, min_lr=1e-9)
    criterion = CrossEntropyLoss()
    best = -1
    num_epochs = configs.epochs

    # 添加早停相关参数
    patience = configs.patience  # 从外部参数获取耐心值
    early_stop_counter = 0  # 早停计数器
    best_epoch = 0  # 最佳模型的epoch

    for epoch in range(num_epochs):
        training_lr = lr_scheduler.get_last_lr()[0]
        train_loss = train_disent_one_epoch(model, train_loader, optimizer, device, criterion, epoch)
        logging.info(f'Epoch {epoch + 1}/{num_epochs}, Loss: {train_loss:.5f},lr: {training_lr}')

        val_loss, all_predictions, all_labels = val_disent_one_epoch(model, val_loader, device, criterion, epoch)
        result = calculate_metric(all_labels, all_predictions, classes)
        lr_scheduler.step(val_loss)

        result.update({'train_loss': train_loss, 'val_loss': val_loss.item(), 'lr': training_lr, 'epoch': epoch})
        append_metrics_to_csv(result, results_file)
        logging.info(f'val epoch {epoch + 1}, result: {result}')

        if run is not None:
            run.log(result)

        # 早停逻辑
        current_score = result['f1-score']
        if current_score > best:
            best = current_score
            best_epoch = epoch
            early_stop_counter = 0  # 重置早停计数器
            torch.save(model.state_dict(), os.path.join(save_dir, 'checkpoints', 'disent.pth'))
            logging.info(f'Best model saved at epoch {epoch + 1} with F1-score: {best:.4f}')
        elif patience > 0 and training_lr < (configs.lr * 0.001):  # 仅当patience>0时执行早停计数
            early_stop_counter += 1
            logging.info(f'Early stopping counter: {early_stop_counter}/{patience}')

            # 如果早停计数器达到耐心值，停止训练
            if early_stop_counter >= patience:
                logging.info(f'Early stopping triggered after {epoch + 1} epochs')
                break

    logging.info(f'Best model was saved at epoch {best_epoch + 1} with F1-score: {best:.4f}')
    model.load_state_dict(torch.load(os.path.join(save_dir, 'checkpoints', 'disent.pth'), weights_only=True, map_location='cpu'))

    # -------------------------- 1. 数据预处理：生成 train/val 标签CSV文件 --------------------------
    # 功能：通过模型处理数据，生成包含类别信息的CSV（后续特征提取依赖此CSV的类别列）
    train_csv = process_and_save_disent(
        model=model,
        data_dir=configs.data_dir,
        device=device,
        transform=transform,
        split='train',  # 数据集划分标识（train/val）
        train_class=configs.train_class,
        factor_index_map_path=configs.factor_index_map_path,  # 统一参数格式（移除多余空格）
        ignore_factors=configs.ignore_factors,
        batch_size=1000,
        save_dir=save_dir
    )

    val_csv = process_and_save_disent(
        model=model,
        data_dir=configs.data_dir,
        device=device,
        transform=transform,
        split='val',
        train_class=configs.train_class,
        factor_index_map_path=configs.factor_index_map_path,
        ignore_factors=configs.ignore_factors,
        batch_size=1000,
        save_dir=save_dir
    )

    # -------------------------- 2. 定义全局路径常量（集中管理，避免重复拼接） --------------------------
    # 原始NPY特征文件根目录（train/val的类别NPY均存于此）
    OVERALL_FEAT_DIR = os.path.join(save_dir, "attributes", "overall_feature_extraction")
    # 提取后语义特征保存根目录（自动匹配train/val子目录）
    SEMANTIC_EMBED_ROOT = os.path.join(save_dir, "attributes", "train_semantic_embed")
    # 类别均值特征保存目录（save_class_mean_features的输出目录）
    AVG_DISENT_FEAT_DIR = os.path.join(save_dir, "attributes", "avg_disent_feats")
    # 特征拼接结果保存目录（concat_fault_features的输出目录）
    SEMANTIC_ATTR_SAVE_DIR = os.path.join(save_dir, "attributes", "semantic_attribute")

    # -------------------------- 3. 批量提取类别特征：调用 extract_class_features --------------------------
    # 功能：按CSV的类别列（Fault Location/Fault Size）划分NPY特征，保存到对应目录
    # 任务参数：(数据集划分, CSV路径, 类别列名)
    extract_tasks = [
        ("train", train_csv, "Fault Location"),
        ("train", train_csv, "Fault Size"),
        ("val", val_csv, "Fault Location"),
        ("val", val_csv, "Fault Size")
    ]

    for split, csv_path, class_col in extract_tasks:
        # 构建当前任务的NPY特征路径（格式：{划分}-{类别列名}.npy）
        npy_file_path = os.path.join(OVERALL_FEAT_DIR, f"{split}-{class_col}.npy")
        # 构建特征保存目录（格式：语义特征根目录/{划分}）
        feat_save_dir = os.path.join(SEMANTIC_EMBED_ROOT, split, class_col)

        # 调用特征提取函数
        extract_class_features(
            csv_path=csv_path,  # 对应数据集的类别CSV
            npy_base_dir=npy_file_path,  # 原始NPY特征文件路径
            name=class_col,  # 双重角色：CSV列名 + NPY文件名核心
            save_dir=feat_save_dir  # 提取后特征的保存目录
        )

    # -------------------------- 4. 批量计算类别均值：调用 save_class_mean_features --------------------------
    # 功能：针对val集NPY特征，按类别计算均值并保存
    # 仅需遍历两个类别列名
    save_tasks = ["Fault Location", "Fault Size"]

    for class_col in save_tasks:
        # 构建val集当前类别的NPY路径（格式：val-{类别列名}.npy）
        val_npy_path = os.path.join(OVERALL_FEAT_DIR, f"train-{class_col}.npy")

        # 调用均值计算函数
        save_class_mean_features(
            encoding_path=val_npy_path,  # val集NPY特征（形状：[样本数, 特征维度]）
            csv_path=train_csv,  # val集类别CSV
            show_feature=class_col,  # 分类依据的类别列名
            save_npy_path=AVG_DISENT_FEAT_DIR  # 均值特征保存目录
        )

    # -------------------------- 5. 批量拼接特征：调用 concat_fault_features --------------------------
    # 功能：拼接「故障位置」和「故障尺寸」的均值特征，生成组合特征
    # 先定义所有故障位置（Location）和故障尺寸（Size）的取值（基于原代码重复调用归纳）
    FAULT_LOCATIONS = ["B", "IR", "OR", "No"]  # 故障位置：B/IR/OR/No
    # 故障尺寸：普通位置（B/IR/OR）对应3个尺寸，No位置对应1个尺寸（0inch）
    FAULT_SIZES = {
        "B": ["007inch", "014inch", "021inch"],
        "IR": ["007inch", "014inch", "021inch"],
        "OR": ["007inch", "014inch", "021inch"],
        "No": ["0inch"]
    }

    # 遍历所有故障位置+尺寸组合，批量拼接特征
    for loc in FAULT_LOCATIONS:
        for size in FAULT_SIZES[loc]:
            # 构建「故障位置」均值特征路径（格式：Fault Location_{位置}.npy）
            loc_feat_path = os.path.join(AVG_DISENT_FEAT_DIR, f"Fault Location_{loc}.npy")
            # 构建「故障尺寸」均值特征路径（格式：Fault Size_{尺寸}.npy）
            size_feat_path = os.path.join(AVG_DISENT_FEAT_DIR, f"Fault Size_{size}.npy")

            # 调用特征拼接函数
            concat_fault_features(
                loc_feat_path,  # 故障位置特征路径
                size_feat_path,  # 故障尺寸特征路径
                SEMANTIC_ATTR_SAVE_DIR  # 拼接结果保存目录
            )

    return save_dir


def process_and_save_disent(model, data_dir, device, transform, split,
                            train_class, factor_index_map_path, ignore_factors, batch_size, save_dir):
    # 1. 执行解纠缠预测
    df, dis, features = disent_predict(
        model=model,
        data_dir=data_dir,
        device=device,
        transform=transform,
        image_subdir=split,  # 区分训练/验证数据
        class_list_path=train_class,
        factor_index_map_path=factor_index_map_path,
        ignore_factors=ignore_factors,
        batch_size=batch_size
    )

    # 2. 确保保存目录存在（避免路径不存在报错）
    npy_save_dir = os.path.join(save_dir, 'attributes', 'overall_feature_extraction')
    os.makedirs(npy_save_dir, exist_ok=True)  # 不存在则创建，存在不报错

    # 3. 保存CSV文件（修正原val数据误用train_df的问题）
    csv_path = os.path.join(save_dir, f'{split}_disent.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    # 4. 保存解纠缠特征NPY文件（统一用split拼接文件名）
    factor_names = ['Operating Condition', 'Fault Location', 'Fault Size']
    for idx, factor_name in enumerate(factor_names):
        npy_path = os.path.join(npy_save_dir, f'{split}-{factor_name}.npy')
        np.save(npy_path, dis[idx])

    return csv_path


def get_disent_args(args=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--class_dims', type=int, nargs='+', default=[3, 4, 4])
    parser.add_argument('--attribute_dim', type=int, default=64)
    parser.add_argument('--ortho_weight', type=float, default=2)

    parser.add_argument('--data_dir', type=str,
                        default=r'/data/coding/dataset/CWRU')

    parser.add_argument('--save_dir', type=str, default=r'/data/coding/output/TaskA_CWRU_01')
    parser.add_argument('--train_class', type=str,
                        default=r'/data/coding/dataset/CWRU/seen_classes.txt')
    parser.add_argument('--factor_index_map_path', type=str,
                        default=r'/data/coding/dataset/CWRU/factor_index_map.txt')
    parser.add_argument('--ignore_factors', type=str, nargs='*', default=None)
    parser.add_argument('--epochs', default=150, type=int)
    parser.add_argument('--batch_size', default=400, type=int)
    parser.add_argument('--lr', default=1e-2, type=float)
    parser.add_argument('--patience', default=10, type=int)
    parser.add_argument('--num_workers', default=os.cpu_count(), type=int)
    parser.add_argument('--prefix', type=str, default='exp')

    return parser.parse_args(args if args else [])


@dataclass
class TrainDisentConfig:
    # 设备与数据变换（添加明确类型注解）
    device: torch.device = field(
        default_factory=get_device,  # 用default_factory延迟初始化，避免模块导入时执行
        metadata={"desc": "训练使用的设备（CPU/GPU）"}
    )
    transform: transforms.Compose = field(
        default_factory=lambda: transforms.Compose([  # 用default_factory创建Compose实例
            transforms.Resize((64, 64)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ]),
        metadata={"desc": "图像预处理变换管道"}
    )
    # 模型核心参数
    class_dims: List[int] = field(
        default_factory=lambda: [3, 4, 4],
        metadata={"desc": "类别维度列表，支持多个整数输入"}
    )
    attribute_dim: int = 64
    ortho_weight: float = 2

    # 路径参数（支持str或Path类型）
    data_dir: Union[str, Path] = r'D:\Code\2-ZSL\0-data\CWRU\dataset'  # 扩展为Union类型
    save_dir: Union[str, Path] = r'D:\Code\2-ZSL\1-output\特征解耦结果'
    train_class: Union[str, Path] = r'D:\Code\2-ZSL\0-data\CWRU\dataset\seen_classes.txt'
    factor_index_map_path: Union[str, Path] = r'D:\Code\2-ZSL\0-data\CWRU\dataset\factor_index_map.txt'
    ignore_factors: Optional[List[str]] = None  # 非路径参数保持不变

    # 训练超参数
    epochs: int = 150
    batch_size: int = 500
    lr: float = 1e-2
    patience: int = 10
    num_workers: int = 0
    # field(
    #     default_factory=lambda: os.cpu_count() or 0,
    #     metadata={"desc": "数据加载进程数，默认使用CPU核心数"}
    # )

    prefix: str = "exp"



if __name__ == '__main__':
    opts = TrainDisentConfig(data_dir=r'D:\Code\2-ZSL\0-data\CWRU\dataset',
                             save_dir=r'D:\Code\2-ZSL\1-output\特征解耦结果',
                             train_class=r'D:\Code\2-ZSL\0-data\CWRU\dataset\seen_classes.txt',
                             factor_index_map_path=r'D:\Code\2-ZSL\0-data\CWRU\dataset\factor_index_map.txt',
                             epochs=5,
                             )
    opts.save_dir = setup_save_dirs(opts.save_dir, opts.prefix)
    logger = setup_logger(opts.save_dir)
    logger.info("=" * 60)
    logger.info("【单独运行】特征解耦网络训练流程")
    logger.info(f"配置信息:{vars(opts)}")
    logger.info("=" * 60)
    train_disent(opts)
