import argparse
import os
import time  # 导入时间计算模块
from dataclasses import dataclass
from typing import Optional, List

from torchvision import transforms

from zsl_ma.tools.predict_untils import euclidean_predict
from zsl_ma.tools.tool import get_device, setup_save_dirs, setup_logger
from zsl_ma.train import train_disent
from zsl_ma.train.train_att_proj import train_proj, TrainAttprojConfig
from zsl_ma.train.train_cls import TrainClsConfig, train_cls
from zsl_ma.train.train_disent import TrainDisentConfig
from zsl_ma.train.train_fea_proj import TrainFeaProjConfig, train_fea_proj


def run(configs):
    # -------------------------- 初始化:整体时间记录+保存目录+日志 --------------------------
    start_total_time = time.perf_counter()  # 整体训练开始时间(高精度)
    save_dir = setup_save_dirs(configs.save_dir, 'exp')
    logger = setup_logger(save_dir)
    logger.info("=" * 60)
    logger.info("开始零样本学习完整训练流程")
    logger.info(f"配置信息:{vars(configs)}")
    logger.info(f"结果保存目录:{save_dir}")
    logger.info("=" * 60)

    # 设备初始化
    device = get_device()
    logger.info(f"使用计算设备:{device.type}(设备ID:{device.index if device.index is not None else '无'})")

    # 统一图像变换配置
    transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    logger.info("图像预处理管道初始化完成:Resize(64,64) → ToTensor → Normalize")

    # -------------------------- 1. 特征解耦训练(含耗时计算) --------------------------
    logger.info("\n" + "=" * 50)
    logger.info("阶段1/4:特征解耦模型训练")
    logger.info("=" * 50)

    # 配置特征解耦参数
    disent_config = TrainDisentConfig(
        device=device,
        transform=transform,
        class_dims=configs.class_dims,
        attribute_dim=configs.attribute_dim,
        save_dir=save_dir,
        data_dir=configs.data_dir,
        train_class=configs.train_class,
        factor_index_map_path=configs.factor_index_map_path,
        batch_size=configs.disent_batch_size,
        epochs=configs.disent_epochs,
        lr=configs.disent_lr,
        patience=configs.disent_patience,
        num_workers=configs.num_workers,
    )
    logger.info(f"特征解耦训练配置:{disent_config}")

    # 记录阶段开始时间
    start_disent = time.perf_counter()
    # 调用训练函数(需确保train_disent内部用logger输出详细日志)
    train_disent.train_disent(disent_config)  # 传入logger,让训练细节写入日志
    # 计算阶段耗时
    end_disent = time.perf_counter()
    disent_time = end_disent - start_disent
    logger.info(f"阶段1完成:特征解耦训练耗时 → {disent_time:.2f}秒({disent_time / 60:.2f}分钟)")

    # -------------------------- 2. 属性投影训练(含耗时计算) --------------------------
    logger.info("\n" + "=" * 50)
    logger.info("阶段2/4:属性投影模型训练")
    logger.info("=" * 50)

    # 配置属性投影参数
    att_proj_opts = TrainAttprojConfig(
        device=device,
        save_dir=save_dir,
        embed_dim=configs.embed_dim,
        attribute_dims=configs.attribute_dim,
        lr=configs.att_proj_lr,
        epochs=configs.att_proj_epochs,
        batch_size=configs.att_proj_batch_size,
        patience=configs.att_proj_patience,
        num_workers=configs.num_workers,
    )
    logger.info(f"属性投影训练配置:{att_proj_opts}")

    # 记录阶段开始时间
    start_att_proj = time.perf_counter()
    # 调用训练函数(传入logger)
    train_proj(att_proj_opts)  # 确保train_proj内部用logger输出
    # 计算阶段耗时
    end_att_proj = time.perf_counter()
    att_proj_time = end_att_proj - start_att_proj
    logger.info(f"阶段2完成:属性投影训练耗时 → {att_proj_time:.2f}秒({att_proj_time / 60:.2f}分钟)")

    # -------------------------- 3. 分类器训练(含耗时计算) --------------------------
    logger.info("\n" + "=" * 50)
    logger.info("阶段3/4:分类器模型训练")
    logger.info("=" * 50)

    # 配置分类器参数
    cls_config = TrainClsConfig(
        device=device,
        transform=transform,
        data_dir=configs.data_dir,
        save_dir=save_dir,
        train_class=configs.train_class,
        num_workers=configs.num_workers,
        epochs=configs.cls_epochs,
        batch_size=configs.cls_batch_size,
        lr=configs.cls_lr,
        patience=configs.cls_patience,
    )
    logger.info(f"分类器训练配置:{cls_config}")

    # 记录阶段开始时间
    start_cls = time.perf_counter()
    # 调用训练函数(传入logger)
    train_cls(cls_config)  # 确保train_cls内部用logger输出
    # 计算阶段耗时
    end_cls = time.perf_counter()
    cls_time = end_cls - start_cls
    logger.info(f"阶段3完成:分类器训练耗时 → {cls_time:.2f}秒({cls_time / 60:.2f}分钟)")

    # -------------------------- 4. 特征投影训练(含耗时计算) --------------------------
    logger.info("\n" + "=" * 50)
    logger.info("阶段4/4:特征投影模型训练")
    logger.info("=" * 50)

    # 配置特征投影参数
    fea_proj_opts = TrainFeaProjConfig(
        device=device,
        transform=transform,
        data_dir=configs.data_dir,
        save_dir=save_dir,
        train_class=configs.train_class,
        factor_index_map_path=configs.factor_index_map_path,
        num_workers=configs.num_workers,
        batch_size=configs.fea_proj_batch_size,
        epochs=configs.fea_proj_epochs,
        lr=configs.fea_proj_lr,
        patience=configs.fea_proj_patience,
    )
    logger.info(f"特征投影训练配置:{fea_proj_opts}")

    # 记录阶段开始时间
    start_fea_proj = time.perf_counter()
    # 调用训练函数(传入logger)
    fea_proj_model = train_fea_proj(fea_proj_opts)  # 确保train_fea_proj内部用logger输出
    # 计算阶段耗时
    end_fea_proj = time.perf_counter()
    fea_proj_time = end_fea_proj - start_fea_proj
    logger.info(f"阶段4完成:特征投影训练耗时 → {fea_proj_time:.2f}秒({fea_proj_time / 60:.2f}分钟)")

    # -------------------------- 5. 预测评估(含耗时计算) --------------------------
    logger.info("\n" + "=" * 50)
    logger.info("额外阶段:测试集预测评估")
    logger.info("=" * 50)

    test_list = configs.test_list
    logger.info(f"待测试集列表:{test_list},预测批次大小:{configs.predict_batch_size}")

    # 记录预测总时间
    total_predict_time = 0.0

    for test_img in test_list:
        try:
            # 单测试集耗时记录
            start_single_pred = time.perf_counter()
            # 执行预测
            df, metrics = euclidean_predict(
                fea_proj_model,
                configs.data_dir,
                os.path.join(save_dir, 'attributes', 'semantic_embed'),
                os.path.join(configs.data_dir, f'{test_img}.txt'),
                configs.factor_index_map_path,
                device,
                transform,
                ignore_factors=['Operating Condition'],
                batch_size=configs.predict_batch_size
            )
            # 单测试集耗时
            end_single_pred = time.perf_counter()
            single_pred_time = end_single_pred - start_single_pred
            total_predict_time += single_pred_time

            # 保存预测结果(日志写入)
            result_path = os.path.join(save_dir, f'{test_img}-预测结果.csv')
            df.to_csv(result_path, index=False, encoding='utf-8-sig')
            logger.info(f"✅ {test_img} 预测完成:")
            logger.info(f"   - 结果文件:{result_path}")
            logger.info("   - 预测指标:")
            logger.info('\n' + metrics)
            logger.info(f"   - 单测试集耗时:{single_pred_time:.2f}秒")

        except Exception as e:
            logger.error(f"❌ {test_img} 预测失败:{e}", exc_info=True)  # exc_info=True记录堆栈信息

    # 总预测耗时
    logger.info(f"额外阶段完成:所有测试集预测总耗时 → {total_predict_time:.2f}秒({total_predict_time / 60:.2f}分钟)")

    # -------------------------- 6. 整体训练流程总结 --------------------------
    logger.info("\n" + "=" * 60)
    logger.info("完整训练流程总结")
    logger.info("=" * 60)

    # 各阶段耗时汇总
    logger.info("各阶段耗时明细:")
    logger.info(f"1. 特征解耦训练:{disent_time:.2f}秒({disent_time / 60:.2f}分钟)")
    logger.info(f"2. 属性投影训练:{att_proj_time:.2f}秒({att_proj_time / 60:.2f}分钟)")
    logger.info(f"3. 分类器训练:{cls_time:.2f}秒({cls_time / 60:.2f}分钟)")
    logger.info(f"4. 特征投影训练:{fea_proj_time:.2f}秒({fea_proj_time / 60:.2f}分钟)")
    logger.info(f"5. 测试集预测:{total_predict_time:.2f}秒({total_predict_time / 60:.2f}分钟)")

    # 整体总耗时
    end_total_time = time.perf_counter()
    total_time = end_total_time - start_total_time
    logger.info(
        f"📊 整体训练与预测流程总耗时 → {total_time:.2f}秒({total_time / 60:.2f}分钟 / {total_time / 3600:.2f}小时)")
    logger.info(f"🎉 所有流程完成！结果统一保存于:{save_dir}")
    logger.info("=" * 60)


def get_train_args(args: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="零样本学习完整训练流程配置(含日志与耗时统计)")

    # 基础路径配置
    parser.add_argument('--data_dir', type=str,
                        default=r'D:\Code\2-ZSL\0-data\CWRU\dataset',
                        help="数据集根目录(含训练/测试数据)")
    parser.add_argument('--save_dir', type=str,
                        default=r'D:\Code\2-ZSL\1-output\特征解耦结果',
                        help="模型、日志、结果文件保存根目录")
    parser.add_argument('--train_class', type=str,
                        default=r'D:\Code\2-ZSL\0-data\CWRU\dataset\seen_classes.txt',
                        help="训练类别列表文件路径(每行一个类别)")
    parser.add_argument('--factor_index_map_path', type=str,
                        default=r'D:\Code\2-ZSL\0-data\CWRU\dataset\factor_index_map.txt',
                        help="因子-索引映射文件路径(用于解耦模型)")

    # 测试配置
    parser.add_argument('--test_list', type=str, nargs='+',
                        default=['0HP', '1HP', '2HP', '3HP'],
                        help="测试集前缀列表(如['0HP','1HP'],对应测试集文件{前缀}.txt)")
    parser.add_argument('--predict_batch_size', type=int, default=1000,
                        help="预测阶段的批次大小(根据显存调整)")

    # 通用配置
    parser.add_argument('--num_workers', type=int, default=0,
                        help="数据加载进程数(Windows建议0,Linux建议CPU核心数-1)")
    parser.add_argument('--attribute_dim', type=int, default=64,
                        help="属性向量维度(解耦模型与属性投影模型共用)")
    parser.add_argument('--embed_dim', type=int, default=512,
                        help="嵌入向量维度(属性投影模型用)")

    # 特征解耦训练配置
    parser.add_argument('--class_dims', type=int, nargs='+', default=[3, 4, 4],
                        help="解耦模型的类别维度列表(如[故障类型数, 负载数, 其他因子数])")
    parser.add_argument('--disent_epochs', type=int, default=1,
                        help="特征解耦模型训练轮数(调试用1,正式训练建议100+)")
    parser.add_argument('--disent_batch_size', type=int, default=20,
                        help="特征解耦训练批次大小(根据显存调整)")
    parser.add_argument('--disent_lr', type=float, default=1e-2,
                        help="特征解耦模型学习率(初始建议1e-2,后期可衰减)")
    parser.add_argument('--disent_patience', type=int, default=10,
                        help="特征解耦早停耐心值(连续10轮无提升则停止)")

    # 属性投影训练配置
    parser.add_argument('--att_proj_epochs', type=int, default=1,
                        help="属性投影模型训练轮数(调试用1,正式训练建议50+)")
    parser.add_argument('--att_proj_batch_size', type=int, default=100,
                        help="属性投影训练批次大小")
    parser.add_argument('--att_proj_lr', type=float, default=1e-3,
                        help="属性投影模型学习率")
    parser.add_argument('--att_proj_patience', type=int, default=10,
                        help="属性投影早停耐心值")

    # 分类器训练配置
    parser.add_argument('--cls_epochs', type=int, default=1,
                        help="分类器模型训练轮数(调试用1,正式训练建议100+)")
    parser.add_argument('--cls_batch_size', type=int, default=40,
                        help="分类器训练批次大小")
    parser.add_argument('--cls_lr', type=float, default=1e-3,
                        help="分类器模型学习率")
    parser.add_argument('--cls_patience', type=int, default=10,
                        help="分类器早停耐心值")

    # 特征投影训练配置
    parser.add_argument('--fea_proj_epochs', type=int, default=2,
                        help="特征投影模型训练轮数(调试用2,正式训练建议150+)")
    parser.add_argument('--fea_proj_batch_size', type=int, default=300,
                        help="特征投影训练批次大小")
    parser.add_argument('--fea_proj_lr', type=float, default=1e-3,
                        help="特征投影模型学习率")
    parser.add_argument('--fea_proj_patience', type=int, default=10,
                        help="特征投影早停耐心值")

    return parser.parse_args(args) if args is not None else parser.parse_args()


@dataclass
class TrainConfig:
    # 特征解耦训练配置
    class_dims: List[int]
    disent_epochs: int = 150
    disent_batch_size: int = 500
    disent_lr: float = 1e-2
    disent_patience: int = 10
    # 基础路径配置
    data_dir: str = r'D:\Code\2-ZSL\0-data\CWRU\dataset'
    save_dir: str = r'D:\Code\2-ZSL\1-output\特征解耦结果'
    train_class: str = r'D:\Code\2-ZSL\0-data\CWRU\dataset\seen_classes.txt'
    factor_index_map_path: str = r'D:\Code\2-ZSL\0-data\CWRU\dataset\factor_index_map.txt'

    # 测试配置
    test_list: List[str] = None  # 用None初始化，后续赋值默认列表
    predict_batch_size: int = 1000

    # 通用配置
    num_workers: int = 0
    attribute_dim: int = 64
    embed_dim: int = 512

    # 属性投影训练配置
    att_proj_epochs: int = 600
    att_proj_batch_size: int = 500
    att_proj_lr: float = 1e-3
    att_proj_patience: int = 10

    # 分类器训练配置
    cls_epochs: int = 100
    cls_batch_size: int = 500
    cls_lr: float = 1e-3
    cls_patience: int = 10

    # 特征投影训练配置
    fea_proj_epochs: int = 150
    fea_proj_batch_size: int = 500
    fea_proj_lr: float = 1e-3
    fea_proj_patience: int = 10

    def __post_init__(self):
        if self.test_list is None:
            self.test_list = ['0HP', '1HP', '2HP', '3HP']


if __name__ == '__main__':
    # opts = get_train_args()
    opts = TrainConfig(class_dims=[3, 4, 4],
                       disent_batch_size=20,
                       att_proj_batch_size=100,
                       cls_batch_size=40,
                       fea_proj_batch_size=100,
                       disent_epochs=2,
                       cls_epochs=2,
                       att_proj_epochs=2,
                       fea_proj_epochs=2,
                       )
    # 打印配置(控制台快速查看,日志会重复记录)
    print("=" * 50)
    print("当前训练配置(命令行参数)")
    print("=" * 50)
    for arg, value in sorted(vars(opts).items()):
        print(f"  --{arg}: {value}")
    print("=" * 50)
    # 启动训练流程
    run(opts)
