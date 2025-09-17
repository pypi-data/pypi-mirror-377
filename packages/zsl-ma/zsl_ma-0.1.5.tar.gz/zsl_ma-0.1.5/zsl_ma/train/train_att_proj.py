import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

import torch
from torch.nn import CrossEntropyLoss
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader

from zsl_ma.dataset_utils.CustomImageDataset import CustomNpyDataset
from zsl_ma.models.projection import AttributeProjectionModel
from zsl_ma.tools.process_single_npy import process_single_npy_files
from zsl_ma.tools.tool import get_device, create_csv, append_metrics_to_csv, calculate_metric, setup_logger
from zsl_ma.tools.train_val_until import train_attr_proj_one_epoch, val_attr_proj_one_epoch
logger = logging.getLogger('zsl_train')

def train_proj(configs):
    # print(configs)
    # device = get_device()
    device = configs.device
    # print(f'Using device: {device}')
    # save_dir, img_dir, model_dir = setup_save_dirs(configs.save_dir, configs.prefix)
    save_dir = configs.save_dir
    results_file = os.path.join(save_dir, 'semantic_projection_metrics.csv')
    metrics = ['epoch', 'train_loss', 'val_loss', 'accuracy', 'precision', 'recall', 'f1-score', 'lr']
    create_csv(metrics, results_file)

    train_dataset = CustomNpyDataset(
        os.path.join(save_dir, 'attributes', 'train_semantic_embed', 'train', 'Fault Location'),
        os.path.join(save_dir, 'attributes', 'train_semantic_embed', 'train', 'Fault Size'))

    val_dataset = CustomNpyDataset(
        os.path.join(save_dir, 'attributes', 'train_semantic_embed', 'val', 'Fault Location'),
        os.path.join(save_dir, 'attributes', 'train_semantic_embed', 'val', 'Fault Size'))
    classes = train_dataset.unique_labels

    train_loader = DataLoader(train_dataset, batch_size=configs.batch_size, shuffle=True,
                              num_workers=configs.num_workers)
    val_loader = DataLoader(val_dataset, batch_size=configs.batch_size, shuffle=True, num_workers=configs.num_workers)

    model = AttributeProjectionModel(attr_dim=configs.attribute_dims * 2, num_classes=len(classes),
                                     embed_dim=configs.embed_dim, ortho_weight=configs.ortho_weight).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=configs.lr)
    criterion = CrossEntropyLoss()
    lr_scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.1, patience=10, min_lr=1e-9)
    best = 1e8
    num_epochs = configs.epochs

    patience = configs.patience  # 从外部参数获取耐心值
    early_stop_counter = 0  # 早停计数器
    best_epoch = 0  # 最佳模型的epoch

    for epoch in range(num_epochs):
        train_dataset.set_epoch(epoch)
        val_dataset.set_epoch(epoch)
        training_lr = lr_scheduler.get_last_lr()[0]
        train_loss, train_accuracy = train_attr_proj_one_epoch(model=model, train_loader=train_loader, device=device,
                                                               optimizer=optimizer, criterion=criterion, epoch=epoch)
        logger.info(f'the epoch {epoch + 1} train loss is {train_loss:.6f}')

        result = val_attr_proj_one_epoch(model=model, val_loader=val_loader,
                                         device=device, criterion=criterion, epoch=epoch)

        metric = calculate_metric(result['y_true'], result['y_pred'], classes)
        logger.info(f'val epoch {epoch + 1}, val loss: {result["val_loss"]:.4f}, accuracy: {metric["accuracy"]:.2%}')
        metric.update({'epoch': epoch, 'train_loss': train_loss, 'val_loss': result['val_loss'], 'lr': training_lr})
        append_metrics_to_csv(metric, results_file)
        lr_scheduler.step(metric['val_loss'])

        # 早停逻辑
        current_score = metric['val_loss']
        if 0< current_score < best:
            best = current_score
            best_epoch = epoch
            early_stop_counter = 0  # 重置早停计数器
            torch.save(model.state_dict(),
                       os.path.join(save_dir, 'checkpoints', 'semantic_projection.pth'))
            logger.info(f'Best model saved at epoch {epoch + 1} with val_loss: {best:.4f}')
        elif patience > 0 and training_lr < (configs.lr * 0.0001):  # 仅当patience>0时执行早停计数
            early_stop_counter += 1
            logger.info(f'Early stopping counter: {early_stop_counter}/{patience}')

            # 如果早停计数器达到耐心值，停止训练
            if early_stop_counter >= patience:
                logger.info(f'Early stopping triggered after {epoch + 1} epochs')
                break

    logger.info(f'Best model was saved at epoch {best_epoch + 1} with val_loss: {best:.4f}')
    model.load_state_dict(torch.load(os.path.join(os.path.join(save_dir, 'checkpoints'), 'semantic_projection.pth')))
    process_single_npy_files(
        source_dir=os.path.join(save_dir, 'attributes', 'semantic_attribute'),
        target_dir=os.path.join(save_dir, 'attributes', 'semantic_embed'),
        model=model,
        device=device,
    )


def get_proj_args(args=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--embed_dim', type=int, default=512)
    parser.add_argument('--attribute_dims', type=int, default=64)
    parser.add_argument('--ortho_weight', type=int, default=15)

    parser.add_argument('--lr', type=float, default=0.1, help='learning rate')
    parser.add_argument('--epochs', type=int, default=600, help='number of epochs')
    parser.add_argument('--batch_size', type=int, default=256)

    parser.add_argument('--save_dir', type=str, default=r'/data/coding/output/TaskA_CWRU_01/exp-1')

    parser.add_argument('--num_workers', default=os.cpu_count(), type=int)
    parser.add_argument('--patience', default=10, type=int)
    return parser.parse_args(args if args else [])

@dataclass
class TrainAttprojConfig:
    # 设备与数据变换（添加明确类型注解）
    device: torch.device = field(
        default_factory=get_device,  # 用default_factory延迟初始化，避免模块导入时执行
        metadata={"desc": "训练使用的设备（CPU/GPU）"}
    )
    # -------------------------- 模型核心参数 --------------------------
    embed_dim: int = 512
    attribute_dims: int = 64
    ortho_weight: int = 15

    # -------------------------- 训练超参数 --------------------------
    lr: float = 0.1
    epochs: int = 600
    batch_size: int = 256

    # -------------------------- 路径参数（支持 str/Path） --------------------------
    save_dir: Union[str, Path] = r'D:\Code\2-ZSL\1-output\特征解耦结果\exp-3'

    # -------------------------- 其他配置参数 --------------------------
    patience: int = 10
    num_workers: int = 0
    # field(
    #     default_factory=lambda: os.cpu_count() or 0,  # 处理 os.cpu_count() 可能为 None 的情况
    #     metadata={"desc": "数据加载进程数，默认等于CPU核心数"}
    # )




if __name__ == '__main__':
    # opts = get_proj_args()
    opts = TrainAttprojConfig(epochs=1)
    logger = setup_logger(opts.save_dir)
    # 打印配置并启动训练（此时会触发设备信息日志）
    logger.info("=" * 60)
    logger.info("【单独运行】属性投影模型训练流程")
    logger.info(f"配置信息:{vars(opts)}")
    logger.info("=" * 60)
    train_proj(opts)
