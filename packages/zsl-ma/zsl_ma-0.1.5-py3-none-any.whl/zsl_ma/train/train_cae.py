import argparse
import os

import torch
from torch.nn import MSELoss
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchvision import transforms

from zsl_ma.dataset_utils.CustomImageDataset import ImageClassificationDataset
from zsl_ma.dataset_utils.dataset import create_dataloaders
from zsl_ma.models.VAE import DRCAE
from zsl_ma.tools.tool import get_device, setup_save_dirs, create_csv, append_metrics_to_csv
from zsl_ma.tools.train_val_until import train_cae_one_epoch


def main(configs):
    device = get_device()
    print(f'Using device: {device}')
    save_dir, img_dir, model_dir = setup_save_dirs(configs.save_dir, configs.prefix)
    results_file = os.path.join(save_dir, 'cae_metrics.csv')
    metrics = ['epoch', 'train_loss', 'val_loss', 'lr']
    create_csv(metrics, results_file)

    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    train_dataset = ImageClassificationDataset(configs.data_dir, transform=transform, train_class=configs.train_class)
    val_dataset = ImageClassificationDataset(configs.data_dir, transform=transform, train_class=configs.train_class,
                                             mode='val')
    train_loader = DataLoader(train_dataset, batch_size=configs.batch_size, shuffle=True,
                              num_workers=configs.num_workers)
    val_loader = DataLoader(val_dataset, batch_size=configs.batch_size, shuffle=False, num_workers=configs.num_workers)



    model = DRCAE().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=configs.lr)
    lr_scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.1, patience=5, min_lr=1e-9)
    criterion = MSELoss()

    best = 1e8
    num_epochs = configs.epochs

    patience = configs.patience  # 从外部参数获取耐心值
    early_stop_counter = 0  # 早停计数器
    best_epoch = 0  # 最佳模型的epoch
    for epoch in range(num_epochs):
        training_lr = lr_scheduler.get_last_lr()[0]

        train_loss, val_loss = train_cae_one_epoch(model, train_loader, val_loader, device, optimizer, criterion, epoch)
        lr_scheduler.step(val_loss)

        print(f'the epoch {epoch + 1} train loss is {train_loss:.6f}, val loss is {val_loss:.6f}')

        metric = {'epoch': epoch, 'train_loss': train_loss, 'val_loss': val_loss, 'lr': training_lr}
        append_metrics_to_csv(metric, results_file)

        current_score = val_loss
        if current_score < best:
            best = current_score
            best_epoch = epoch
            early_stop_counter = 0  # 重置早停计数器
            model.save_encoder(os.path.join(model_dir, 'encoder.pth'))
            print(f'Best model saved at epoch {epoch + 1} with loss: {best:.6f}')
        elif patience > 0 and training_lr < (configs.lr * 0.0001):  # 仅当patience>0时执行早停计数
            early_stop_counter += 1
            print(f'Early stopping counter: {early_stop_counter}/{patience}')

            # 如果早停计数器达到耐心值，停止训练
            if early_stop_counter >= patience:
                print(f'Early stopping triggered after {epoch + 1} epochs')
                print(f'Best model was saved at epoch {best_epoch + 1} with F1-score: {best:.6f}')
                break



def get_cae_args(args=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data_dir', type=str,
                        default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\CWRU')
    parser.add_argument('--save_dir', type=str, default=r'D:\Code\2-ZSL\1-output\论文实验结果\TaskA_CWRU_06\exp-1')
    parser.add_argument('--train_class', type=str,
                        default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\CWRU/seen_classes.txt')
    parser.add_argument('--epochs', default=200, type=int)
    parser.add_argument('--batch_size', default=100, type=int)
    parser.add_argument('--lr', default=1e-1, type=float)
    parser.add_argument('--weight_decay', default=1e-5, type=float)
    parser.add_argument('--patience', default=10, type=int)
    parser.add_argument('--num_workers', default=0, type=int)
    parser.add_argument('--prefix', type=str, default=None)

    return parser.parse_args(args if args else [])


if __name__ == '__main__':
    opts = get_cae_args()
    print(opts)
    main(opts)
