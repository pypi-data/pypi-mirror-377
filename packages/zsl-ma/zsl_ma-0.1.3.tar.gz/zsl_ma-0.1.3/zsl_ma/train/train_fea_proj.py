import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, List

import numpy as np
import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchvision import transforms

from zsl_ma.dataset_utils.CustomImageDataset import ImageClassificationDataset
from zsl_ma.models.projection import FeatureProjectionModel, LSELoss, EuclideanDistanceLoss, DistanceLoss
from zsl_ma.tools.tool import get_device, create_csv, calculate_metric, append_metrics_to_csv, setup_logger
from zsl_ma.tools.train_val_until import train_cls_one_epoch, eval_cls_one_epoch, eval_fea_proj_epoch, \
    train_fea_proj_one_epoch

logger = logging.getLogger('zsl_train')


def train_fea_proj(configs):
    # print(configs)
    # device = get_device()
    device = configs.device
    transform = configs.transform
    save_dir = configs.save_dir
    results_file = os.path.join(save_dir, 'feature_projection_metrics.csv')
    metrics = ['epoch', 'train_loss', 'val_loss', 'accuracy', 'precision', 'recall', 'f1-score', 'lr']
    create_csv(metrics, results_file)

    # transform = transforms.Compose([transforms.Resize((64, 64)),
    #                                 transforms.ToTensor(),
    #                                 transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    train_dataset = ImageClassificationDataset(configs.data_dir, transform=transform, train_class=configs.train_class,
                                               ignore_factors=configs.ignore_factors,
                                               factor_index_map_path=configs.factor_index_map_path)
    val_dataset = ImageClassificationDataset(configs.data_dir, transform=transform, train_class=configs.train_class,
                                             mode='val', ignore_factors=configs.ignore_factors,
                                             factor_index_map_path=configs.factor_index_map_path)

    train_loader = DataLoader(train_dataset, batch_size=configs.batch_size, shuffle=True,
                              num_workers=configs.num_workers)
    val_loader = DataLoader(val_dataset, batch_size=configs.batch_size, shuffle=False, num_workers=configs.num_workers)
    classes = train_dataset.classes

    semantic_attr_list = []
    for cls_name in classes:
        # npy_path = os.path.join(configs.semantic_path, f"{cls_name}.npy")
        npy_path = os.path.join(save_dir, 'attributes', 'semantic_embed', f'{cls_name}.npy')
        cls_attr = np.load(npy_path, allow_pickle=True)  # 读取单个类别特征
        semantic_attr_list.append(cls_attr)

    semantic_attributes = torch.tensor(np.array(semantic_attr_list, dtype=np.float32), dtype=torch.float32)

    model = FeatureProjectionModel(cnn_path=os.path.join(save_dir, 'checkpoints', 'cnn.pth'),
                                   embed_dim=configs.embed_dim).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=configs.lr)
    criterion = EuclideanDistanceLoss(semantic_attributes).to(device)
    # criterion = DistanceLoss(semantic_attributes, 'cosine').to(device)
    lr_scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.1, patience=5, min_lr=1e-9)
    best = -1
    num_epochs = configs.epochs

    patience = configs.patience  # 从外部参数获取耐心值
    early_stop_counter = 0  # 早停计数器
    best_epoch = 0  # 最佳模型的epoch

    for epoch in range(num_epochs):
        training_lr = lr_scheduler.get_last_lr()[0]
        train_loss, train_accuracy = train_fea_proj_one_epoch(model=model, train_loader=train_loader, device=device,
                                                              optimizer=optimizer, criterion=criterion, epoch=epoch,
                                                              semantic_attributes=semantic_attributes)
        logger.info(f'Epoch {epoch + 1}/{num_epochs}, Loss: {train_loss:.5f}, Train Accuracy: {train_accuracy:.4%},'
              f'lr: {training_lr}')

        result = eval_fea_proj_epoch(model=model, val_loader=val_loader,
                                     device=device, criterion=criterion, epoch=epoch,
                                     semantic_attributes=semantic_attributes)

        metric = calculate_metric(result['y_true'], result['y_pred'], classes)
        logger.info(f'val epoch {epoch + 1}, val loss: {result["val_loss"]:.4f}, accuracy: {metric["accuracy"]:.2%}')
        metric.update({'epoch': epoch, 'train_loss': train_loss, 'val_loss': result['val_loss'], 'lr': training_lr})
        append_metrics_to_csv(metric, results_file)
        lr_scheduler.step(metric['val_loss'])

        # 早停逻辑
        current_score = metric['f1-score']
        if current_score > best and epoch > 0:
            best = current_score
            best_epoch = epoch
            early_stop_counter = 0  # 重置早停计数器
            torch.save(model.state_dict(), os.path.join(save_dir, 'checkpoints', 'feature_projection.pth'))
            logger.info(f'Best model saved at epoch {epoch + 1} with F1-score: {best:.4f}')
        elif patience > 0 and training_lr < (configs.lr * 0.001):  # 仅当patience>0时执行早停计数
            early_stop_counter += 1
            logger.info(f'Early stopping counter: {early_stop_counter}/{patience}')
            # 如果早停计数器达到耐心值，停止训练
            if early_stop_counter >= patience:
                logger.info(f'Early stopping triggered after {epoch + 1} epochs')
                break

    logger.info(f'Best model was saved at epoch {best_epoch + 1} with F1-score: {best:.4f}')

    model.load_state_dict(torch.load(os.path.join(save_dir, 'checkpoints', 'feature_projection.pth')))
    return model


def get_fea_proj_args(args=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data_dir', type=str,
                        default=r'/data/coding/dataset/CWRU')
    parser.add_argument('--save_dir', type=str,
                        default=r'/data/coding/output/TaskA_CWRU_01/exp-1')
    parser.add_argument('--train_class', type=str,
                        default=r'/data/coding/dataset/CWRU/seen_classes.txt')
    parser.add_argument('--factor_index_map_path', type=str,
                        default=r'/data/coding/dataset/CWRU/factor_index_map.txt')
    parser.add_argument('--ignore_factors', type=str, nargs='+', default=['Operating Condition'])

    parser.add_argument('--embed_dim', type=int, default=512)
    parser.add_argument('--epochs', default=150, type=int)
    parser.add_argument('--batch_size', default=600, type=int)
    parser.add_argument('--lr', default=1e-3, type=float)
    parser.add_argument('--weight_decay', default=1e-5, type=float)
    parser.add_argument('--patience', default=10, type=int)
    parser.add_argument('--num_workers', default=os.cpu_count()-1, type=int)

    return parser.parse_args(args if args else [])

@dataclass
class TrainFeaProjConfig:
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
    # -------------------------- 路径参数（支持 str/Path 类型）--------------------------
    data_dir: Union[str, Path] = r'D:\Code\2-ZSL\0-data\CWRU\dataset'  # 扩展为Union类型
    save_dir: Union[str, Path] = r'D:\Code\2-ZSL\1-output\特征解耦结果\exp-3'
    train_class: Union[str, Path] = r'D:\Code\2-ZSL\0-data\CWRU\dataset\seen_classes.txt'
    factor_index_map_path: Union[str, Path] = r'D:\Code\2-ZSL\0-data\CWRU\dataset\factor_index_map.txt'

    # -------------------------- 可变默认值参数（列表用 default_factory）--------------------------
    ignore_factors: List[str] = field(
        default_factory=lambda: ['Operating Condition'],  # 匹配 argparse 的 nargs='+' 默认值
        metadata={"desc": "需要忽略的因素列表，支持多个字符串输入"}
    )

    # -------------------------- 模型与训练超参数 --------------------------
    embed_dim: int = 512
    epochs: int = 150
    batch_size: int = 100
    lr: float = 1e-3
    weight_decay: float = 1e-5
    patience: int = 10
    num_workers: int =0
    # field(
    #     # 处理 os.cpu_count() 为 None 的情况，避免减1报错
    #     default_factory=lambda: (os.cpu_count() - 1) if (os.cpu_count() and os.cpu_count() > 1) else 0,
    #     metadata={"desc": "数据加载进程数，默认 CPU核心数-1（至少1个，避免0进程）"}
    # )


if __name__ == '__main__':
    # opts = get_fea_proj_args()
    opts = TrainFeaProjConfig(epochs=2)
    logger = setup_logger(opts.save_dir)
    # 打印配置并启动训练（此时会触发设备信息日志）
    logger.info("=" * 60)
    logger.info("【单独运行】分类器训练流程")
    logger.info(f"配置信息:{vars(opts)}")
    logger.info("=" * 60)
    train_fea_proj(opts)
