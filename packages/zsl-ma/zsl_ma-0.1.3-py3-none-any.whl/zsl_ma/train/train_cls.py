import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, Optional

import torch
from torch.nn import CrossEntropyLoss
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchvision import transforms

from zsl_ma.dataset_utils.CustomImageDataset import ImageClassificationDataset
from zsl_ma.models.CNN import create_resnet
from zsl_ma.tools.tool import get_device, create_csv, calculate_metric, \
    append_metrics_to_csv, setup_logger
from zsl_ma.tools.train_val_until import train_cls_one_epoch, eval_cls_one_epoch

logger = logging.getLogger('zsl_train')


def train_cls(configs, run=None):
    device = configs.device
    transform = configs.transform
    save_dir = configs.save_dir
    results_file = os.path.join(save_dir, 'cls_metrics.csv')
    metrics = ['epoch','train_loss', 'val_loss', 'accuracy', 'precision', 'recall', 'f1-score', 'lr']
    create_csv(metrics, results_file)

    train_dataset = ImageClassificationDataset(configs.data_dir, transform=transform, train_class=configs.train_class)
    val_dataset = ImageClassificationDataset(configs.data_dir, transform=transform, train_class=configs.train_class,
                                             mode='val')
    train_loader = DataLoader(train_dataset, batch_size=configs.batch_size, shuffle=True,
                              num_workers=configs.num_workers)
    val_loader = DataLoader(val_dataset, batch_size=configs.batch_size, shuffle=False, num_workers=configs.num_workers)

    classes = train_dataset.classes

    model = create_resnet(num_classes=len(classes))
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=configs.lr)
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
        train_loss, train_accuracy = train_cls_one_epoch(model=model, train_loader=train_loader, device=device,
                                                         optimizer=optimizer, criterion=criterion, epoch=epoch)
        logger.info(f'Epoch {epoch + 1}/{num_epochs}, Loss: {train_loss:.5f}, Train Accuracy: {train_accuracy:.4%},'
              f'lr: {training_lr}')

        result = eval_cls_one_epoch(model=model, val_loader=val_loader,
                                    device=device, criterion=criterion, epoch=epoch)

        metric = calculate_metric(result['y_true'], result['y_pred'], classes)
        logger.info(f'val epoch {epoch + 1}, val loss: {result["val_loss"]:.4f}, accuracy: {metric["accuracy"]:.2%}')
        metric.update({'epoch': epoch, 'train_loss': train_loss, 'val_loss': result['val_loss'], 'lr': training_lr})
        append_metrics_to_csv(metric, results_file)
        lr_scheduler.step(metric['val_loss'])

        if run is not None:
            run.log(metric)

        # 早停逻辑
        current_score = metric['f1-score']
        if current_score > best:
            best = current_score
            best_epoch = epoch
            early_stop_counter = 0  # 重置早停计数器
            torch.save(model.state_dict(), os.path.join(save_dir, 'checkpoints', 'cnn.pth'))
            logger.info(f'Best model saved at epoch {epoch + 1} with F1-score: {best:.4f}')
        elif patience > 0 and training_lr < (configs.lr * 0.001):  # 仅当patience>0时执行早停计数
            early_stop_counter += 1
            logger.info(f'Early stopping counter: {early_stop_counter}/{patience}')

            # 如果早停计数器达到耐心值，停止训练
            if early_stop_counter >= patience:
                logger.info(f'Early stopping triggered after {epoch + 1} epochs')
                break

    logger.info(f'Best model was saved at epoch {best_epoch + 1} with F1-score: {best:.4f}')
    # model.load_state_dict(torch.load(os.path.join(model_dir, 'cnn.pth'), weights_only=True, map_location='cpu'))
    #
    # return save_dir, model


def get_cls_args(args=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data_dir', type=str,
                        default=r'/data/coding/dataset/CWRU')
    parser.add_argument('--save_dir', type=str, default=r'/data/coding/output/TaskA_CWRU_01/exp-1')
    parser.add_argument('--train_class', type=str,
                        default=r'/data/coding/dataset/CWRU/seen_classes.txt')
    parser.add_argument('--epochs', default=100, type=int)
    parser.add_argument('--batch_size', default=700, type=int)
    parser.add_argument('--lr', default=1e-3, type=float)
    parser.add_argument('--weight_decay', default=1e-5, type=float)
    parser.add_argument('--patience', default=10, type=int)
    parser.add_argument('--num_workers', default=os.cpu_count()-1, type=int)
    parser.add_argument('--prefix', type=str, default=None)

    return parser.parse_args(args if args else [])



@dataclass
class TrainClsConfig:
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
    # -------------------------- 路径参数--------------------------
    data_dir: Union[str, Path] = r'D:\Code\2-ZSL\0-data\CWRU\dataset'  # 扩展为Union类型
    save_dir: Union[str, Path] = r'D:\Code\2-ZSL\1-output\特征解耦结果\exp-3'
    train_class: Union[str, Path] = r'D:\Code\2-ZSL\0-data\CWRU\dataset\seen_classes.txt'

    # -------------------------- 训练超参数--------------------------
    epochs: int = 100
    batch_size: int = 40
    lr: float = 1e-3
    weight_decay: float = 1e-5
    patience: int = 10
    prefix: Optional[str] = None

    num_workers: int = 0
    # field(
    #     default_factory=lambda:
    #     (os.cpu_count()) if (os.cpu_count() and os.cpu_count() > 1) else 0,
    #     metadata={"desc": "数据加载进程数，默认 CPU核心数-1（避免负数值或None，最低为0）"}
    # )



if __name__ == '__main__':
    # opts = get_cls_args()
    opts = TrainClsConfig(epochs=1)
    logger = setup_logger(opts.save_dir)
    # 打印配置并启动训练（此时会触发设备信息日志）
    logger.info("=" * 60)
    logger.info("【单独运行】分类器训练流程")
    logger.info(f"配置信息:{vars(opts)}")
    logger.info("=" * 60)
    train_cls(opts)
