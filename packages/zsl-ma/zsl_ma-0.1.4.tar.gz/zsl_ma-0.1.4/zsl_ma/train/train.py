import argparse
import os

import torch
from torchvision import transforms

from zsl_ma.models.projection import FeatureProjectionModel
from zsl_ma.tools.predict_untils import euclidean_predict
from zsl_ma.tools.tool import get_device
from zsl_ma.train import train_disent
from zsl_ma.train.train_att_proj import train_proj, TrainAttprojConfig
from zsl_ma.train.train_cls import TrainClsConfig, train_cls
from zsl_ma.train.train_disent import TrainDisentConfig
from zsl_ma.train.train_fea_proj import TrainFeaProjConfig, train_fea_proj


def run(configs):
    device = get_device()
    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    disent_config = TrainDisentConfig(device,transform,
                                      class_dims=configs.class_dims,
                                      attribute_dim=configs.attribute_dim,
                                      save_dir=configs.save_dir,
                                      data_dir=configs.data_dir,
                                      train_class=configs.train_class,
                                      factor_index_map_path=configs.factor_index_map_path,
                                      batch_size=400,
                                      epochs=150,
                                      num_workers=os.cpu_count(),
                                      )
    save_dir = train_disent.train_disent(disent_config)

    att_proj_opts = TrainAttprojConfig(device, save_dir=save_dir)
    train_proj(att_proj_opts)

    cls_config=TrainClsConfig(device, transform,
                              data_dir=configs.data_dir,
                              save_dir=save_dir,
                              train_class=configs.train_class,
                              num_workers=os.cpu_count(),
                              epochs=100,
                              batch_size=700,
                              )
    train_cls(cls_config)

    fae_proj_opts = TrainFeaProjConfig(device, transform,
                                       data_dir=configs.data_dir,
                                       save_dir=save_dir,
                                       train_class=configs.train_class,
                                       factor_index_map_path=configs.factor_index_map_path,
                                       num_workers=os.cpu_count(),
                                       batch_size=600,
                                       epochs=150,
                                       )
    fea_proj_model = train_fea_proj(fae_proj_opts)
    test_list = ['0HP', '1HP', '2HP', '3HP']
    for test_img in test_list:
        df, _ = euclidean_predict(fea_proj_model,
                                  configs.data_dir,
                                  os.path.join(save_dir, 'attributes', 'semantic_embed'),
                                  os.path.join(configs.data_dir, f'{test_img}.txt'),
                                  # rf'/data/coding/dataset/CWRU/{test_img}.txt',
                                  configs.factor_index_map_path,
                                  device,
                                  transform,
                                  ignore_factors=['Operating Condition'],
                                  batch_size=1000
                                  )
        df.to_csv(os.path.join(save_dir, f'{test_img}-预测结果.csv'), index=False, encoding='utf-8-sig')






def get_train_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str,
                        default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen')
    parser.add_argument('--save_dir', type=str, default=r'D:\Code\2-ZSL\1-output\特征解耦结果')
    parser.add_argument('--train_class', type=str,
                        default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen\train_class.txt')
    parser.add_argument('--classes', type=str,
                        default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen\zsl_classes.txt')

    return parser.parse_args(args if args else [])


if __name__ == '__main__':
    print()

    # image_subdir = 'val'


