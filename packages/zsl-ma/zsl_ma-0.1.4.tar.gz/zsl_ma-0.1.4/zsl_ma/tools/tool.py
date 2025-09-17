import logging
import os
import re
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from typing import Tuple, Optional

import numpy as np
import pandas as pd
import pytz
import torch
import wandb
from IPython.core.getipython import get_ipython
from IPython.display import FileLink, display
from sklearn.metrics import classification_report

from zsl_ma.dataset_utils.FactorLabelMapper import FactorLabelMapper, load_class_list

# 配置日志(确保所有输出统一写入文件+控制台)
def setup_logger(save_dir: str) -> logging.Logger:
    """设置训练过程的日志记录(控制台+文件双输出)"""
    logger = logging.getLogger('zsl_train')
    logger.setLevel(logging.INFO)
    logger.propagate = False  # 避免重复输出(防止root logger二次捕获)
    if logger.hasHandlers():
        logger.handlers.clear()

    # 日志格式(包含时间、级别、信息,精确到毫秒)
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # 1. 控制台输出 handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. 文件输出 handler(按时间命名,避免覆盖)
    log_file = os.path.join(save_dir, f'train_log_{time.strftime("%Y%m%d_%H%M%S")}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')  # 支持中文
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info(f'当前日志记录在{log_file}文件中')

    return logger

def setup_save_dirs(parent_dir: str, prefix: Optional[str]=None) :
    """
    目录创建函数：若目录创建失败，直接抛出异常终止程序，而非返回None。
    功能：
    1. 若prefix不为None：在parent_dir下创建「前缀-数字」格式的编号文件夹（如"exp-1"）。
    2. 若prefix为None：直接使用parent_dir作为根保存目录。
    3. 统一创建子目录：images、checkpoints、attributes（含三级子目录：avg_disent_feats、semantic_attribute、semantic_embed）。

    参数:
        parent_dir: 父目录路径（对应configs.save_dir）
        prefix: 文件夹前缀（对应configs.prefix，可为None）

    返回:
        Tuple[save_dir, img_dir, model_dir]: 成功创建的根目录、图像目录、模型目录路径。
        （若失败，会直接抛出异常，不会返回）
    """
    # ------------------------------
    # 1. 确保父目录存在（不存在则创建，失败则抛异常）
    # ------------------------------
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)  # 失败时抛出 OSError（如权限不足、路径无效）

    # ------------------------------
    # 2. 确定根保存目录 save_dir
    # ------------------------------
    if prefix is None:
        save_dir = parent_dir
    else:
        # 正则匹配现有编号文件夹（如"exp-1"）
        escaped_prefix = re.escape(prefix)
        pattern = re.compile(f'^{escaped_prefix}-(\\d+)$')
        existing_numbers = []

        # 收集现有有效编号
        for item in os.listdir(parent_dir):
            item_path = os.path.join(parent_dir, item)
            if os.path.isdir(item_path):
                match = pattern.match(item)
                if match:
                    try:
                        existing_numbers.append(int(match.group(1)))
                    except ValueError:
                        continue  # 忽略数字部分无效的文件夹（如"exp-abc"）

        # 计算下一个可用编号
        if not existing_numbers:
            next_number = 1
        else:
            existing_numbers.sort()
            next_number = 1
            for num in existing_numbers:
                if num > next_number:
                    break
                next_number = num + 1

        # 创建编号文件夹（若已存在，抛 FileExistsError）
        new_folder_name = f"{prefix}-{next_number}"
        save_dir = os.path.join(parent_dir, new_folder_name)
        os.makedirs(save_dir, exist_ok=False)  # exist_ok=False 确保文件夹不存在时才创建

    # ------------------------------
    # 3. 创建子目录（images、checkpoints、attributes及其三级子目录）
    # ------------------------------
    img_dir = os.path.join(save_dir, "images")
    model_dir = os.path.join(save_dir, "checkpoints")
    attr_dir = os.path.join(save_dir, "attributes")
    sub_attr_dirs = [
        os.path.join(attr_dir, "avg_disent_feats"),
        os.path.join(attr_dir, "semantic_attribute"),
        os.path.join(attr_dir, "semantic_embed"),
        os.path.join(attr_dir, "overall_feature_extraction"),
        os.path.join(attr_dir, "train_semantic_embed"),
        os.path.join(attr_dir, "train_semantic_embed", 'train'),
        os.path.join(attr_dir, "train_semantic_embed", 'val'),
    ]

    # 允许子目录已存在（exist_ok=True），但其他错误（如权限不足）仍抛异常
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(attr_dir, exist_ok=True)
    for sub_dir in sub_attr_dirs:
        os.makedirs(sub_dir, exist_ok=True)

    return save_dir


def make_save_dirs(root_dir):
    img_dir = os.path.join(root_dir, 'images')
    model_dir = os.path.join(root_dir, 'checkpoints')
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)
    return img_dir, model_dir


def get_device():
    return torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')


def calculate_metric(all_labels, all_predictions, classes, class_metric=False, average='macro avg'):
    metric = classification_report(y_true=all_labels, y_pred=all_predictions, target_names=classes, labels=np.unique(all_labels)
                                   , digits=4, output_dict=True)
    if not class_metric:
        metric = {
            'accuracy': metric.get('accuracy'),
            'precision': metric.get(average).get('precision'),
            'recall': metric.get(average).get('recall'),
            'f1-score': metric.get(average).get('f1-score'),
        }
        return metric
    else:
        return metric


def get_wandb_runs(
        project_path: str,
        default_name: str = "未命名",
        api_key: Optional[str] = None,
        per_page: int = 1000
) -> List[Dict[str, str]]:
    """
    获取指定 WandB 项目的所有运行信息（ID 和 Name）

    Args:
        project_path (str): 项目路径,格式为 "username/project_name"
        default_name (str): 当运行未命名时的默认显示名称（默认:"未命名"）
        api_key (str, optional): WandB API 密钥,若未设置环境变量则需传入
        per_page (int): 分页查询每页数量（默认1000,用于处理大量运行）

    Returns:
        List[Dict]: 包含运行信息的字典列表,格式 [{"id": "...", "name": "..."}]

    Raises:
        ValueError: 项目路径格式错误
        wandb.errors.UsageError: API 密钥无效或未登录
    """
    # 参数校验
    if "/" not in project_path or len(project_path.split("/")) != 2:
        raise ValueError("项目路径格式应为 'username/project_name'")

    # 登录（仅在需要时）
    if api_key:
        wandb.login(key=api_key)
    elif not wandb.api.api_key:
        raise wandb.errors.UsageError("需要提供API密钥或预先调用wandb.login()")

    # 初始化API
    api = wandb.Api()

    try:
        # 分页获取所有运行（自动处理分页逻辑）
        runs = api.runs(project_path, per_page=per_page)
        print(f'共获取{len(runs)}个run')
        result = [
            {
                "id": run.id,
                "name": run.name or default_name,
                "url": run.url,  # 增加实用字段
                "state": run.state,  # 包含运行状态
                "time": run.metadata['startedAt']
            }
            for run in runs
        ]
        beijing_tz = pytz.timezone('Asia/Shanghai')
        for res in result:
            res["time"] = (
                datetime.strptime(res["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
                .replace(tzinfo=pytz.utc)
                .astimezone(beijing_tz)
                .strftime("%Y-%m-%d %H:%M:%S.%f")
            )
        result.sort(key=lambda x: x["time"], reverse=True)
        return result

    except wandb.errors.CommError as e:
        raise ConnectionError(f"连接失败: {str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"获取运行数据失败: {str(e)}") from e


def get_id(target_name, res):
    df = pd.DataFrame.from_records(res)
    # 筛选状态既不是 'finished' 也不是 'running' 的记录
    filtered = df[(df['name'] == target_name) & ~df['state'].isin(['finished', 'running'])]['id']

    if not filtered.empty:
        # 存在符合条件的记录,返回第一个 id
        return filtered.iloc[0]
    else:
        # 无符合条件的记录,获取该 name 最新的 id（按 id 降序排列取第一个）
        name_df = df[df['name'] == target_name]
        if name_df.empty:
            return '001'  # 无该 name 的任何记录时返回 None
        latest_id_str = name_df['id'].iloc[0]
        # 转为数值加 1 后再格式化为三位字符串
        new_id_num = int(latest_id_str) + 1
        return f"{new_id_num:03d}"


def get_all_projects(entity: str = None, api_key: str = None, verbose: bool = True) -> List[Dict[str, Any]]:
    """
    获取WandB账户中所有的project

    参数:
        entity: WandB实体名称（团队或用户名）,如果为None则使用默认实体
        api_key: WandB API密钥,如果为None则使用环境变量或配置文件中的密钥
        verbose: 是否打印进度信息

    返回:
        包含所有project信息的字典列表
    """
    # 初始化WandB API
    api = wandb.Api(api_key=api_key)

    # 如果未指定实体,获取默认实体
    if entity is None:
        try:
            entity = api.default_entity
            if verbose:
                print(f"使用默认实体: {entity}")
        except Exception as e:
            raise ValueError("未指定实体且无法获取默认实体,请提供entity参数或配置默认实体") from e

    # 存储所有项目的列表
    all_projects = []

    if verbose:
        print(f"开始获取实体 {entity} 下的所有项目...")

    try:
        # 直接迭代获取所有项目
        projects = api.projects(entity=entity)
        for idx, project in enumerate(projects):
            project_info = {
                "id": project.id,
                "name": project.name,
                "entity": project.entity,
                "created_at": project.created_at,
                "url": project.url,
            }
            all_projects.append(project_info)

            if verbose and (idx + 1) % 10 == 0:
                print(f"已获取 {idx + 1} 个项目")


    except Exception as e:
        print(f"获取项目时出错: {e}")

    if verbose:
        print(f"总共获取了 {len(all_projects)} 个项目")

    return all_projects


def natural_sort_key(s: str) -> list:
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]


def generate_zsl_image_dataframe(root_dir: str,
                                 test_image_class,
                                 predict_class_file=None  # 修改为可选参数，默认None
                                 ):
    image_classes = load_class_list(test_image_class)

    # 处理predict_classes：若predict_class_file为空，则使用image_classes
    if predict_class_file is None or not predict_class_file:
        predict_classes = image_classes
    else:
        predict_classes = load_class_list(predict_class_file)

    class_to_idx = {cls: idx for idx, cls in enumerate(predict_classes)}
    image_root_dir = os.path.join(root_dir, 'val')

    full_image_paths = []  # 图片完整路径
    targets = []  # 标注类别ID（映射器中的索引）
    class_names = []  # 标注类别名称
    label_names = []

    for class_name in image_classes:
        # 构建当前类别的图片文件夹路径（image_root_dir / 类别名）
        class_img_dir = os.path.join(image_root_dir, class_name)
        # 收集该类别下的所有图片（筛选指定后缀）
        image_extensions = ('.bmp', '.jpg', '.jpeg', '.png')  # 支持的图片后缀
        class_images = [
            img for img in os.listdir(class_img_dir)
            if img.lower().endswith(image_extensions)  # 忽略大小写（如.IMG/.JPG）
        ]

        # 对图片按自然排序（保证顺序一致性）
        class_images_sorted = sorted(class_images, key=natural_sort_key)

        # 图片完整路径（类别文件夹路径 + 图片名）
        class_image_paths = [os.path.join(class_img_dir, img) for img in class_images_sorted]

        # 处理class_id：若predict_class_file为空，则class_id=class_name，否则按原逻辑处理
        if predict_class_file is None or not predict_class_file:
            class_id = class_name  # 关键修改：predict_class_file为空时，class_id直接使用class_name
        else:
            prefix_part = class_name.split("_")[0]  # 提取"0-No"或"0-B-007"
            parts = prefix_part.split("-")  # 按"-"分割为列表
            class_id = "-".join(parts[1:])

        class_target = class_to_idx[class_id]

        # 批量添加基础信息到列表
        full_image_paths.extend(class_image_paths)
        targets.extend([class_target] * len(class_images_sorted))
        class_names.extend([class_name] * len(class_images_sorted))
        label_names.extend([class_id] * len(class_images_sorted))

    # 构建基础DataFrame（必选列）
    columns = {
        '图片路径': full_image_paths,
        '标注类别ID': targets,
        '标注类别名称': class_names,
        '标签名称': label_names
    }
    return pd.DataFrame(columns)


def generate_image_dataframe(root_dir: str,
                             image_subdir: str,
                             class_list_path: Optional[str] = None,
                             factor_index_map_path: Optional[str] = None,
                             ignore_factors=None,
                             need_parse_factors=True) -> Tuple[pd.DataFrame, 'FactorLabelMapper']:
    """
    生成包含图片完整信息及可选因子数据的数据框（适配图片按类别分文件夹存放的场景）
    自动拼接“因子值+单位”（如0→0HP、007→007英寸），且因子列按“值列集中+编码列集中”排序

    参数:
        root_dir: str - FactorLabelMapper所需的根目录（用于加载类别映射）
        image_subdir: str - 存放类别文件夹的父目录（位于root_dir下,如"images"）
        class_list_path: Optional[str] - 类别列表txt路径（可选,传给FactorLabelMapper）
        factor_index_map_path: Optional[str] - 因子索引映射文件路径（**决定是否解析因子**）
                                              若提供则开启因子解析，否则仅保留基础信息

    返回:
        Tuple[pd.DataFrame, FactorLabelMapper]:
            - pd.DataFrame: 列顺序为【基础列→所有因子值列→所有因子编码列】
            - FactorLabelMapper: 初始化后的类别-因子映射器（含因子单位信息）
    """
    # 初始化类别-因子映射器（核心：由factor_index_map_path决定是否解析因子）
    mapper = FactorLabelMapper(
        data_dir=root_dir,
        class_list_path=class_list_path,
        factor_index_map_path=factor_index_map_path,  # 映射器通过该参数判断是否开启parse_factors
        ignore_factors=ignore_factors
    )
    valid_classes = mapper.raw_classes  # 映射器加载的有效类别列表
    # need_parse_factors = mapper.parse_factors  # 从映射器获取是否需要解析因子
    num_factors = mapper.num_factors if need_parse_factors else 0  # 因子数量

    # ------------------------------
    # 1. 验证图片根目录（image_subdir）
    # ------------------------------
    image_root_dir = os.path.join(root_dir, image_subdir)
    if not os.path.exists(image_root_dir):
        raise ValueError(f"❌ 图片根目录不存在:{image_root_dir}\n请检查image_subdir参数是否正确")

    # ------------------------------
    # 2. 初始化数据收集列表
    # ------------------------------
    # 基础信息列表（所有场景必选）
    full_image_paths = []  # 图片完整路径
    targets = []  # 标注类别ID（映射器中的索引）
    class_names = []  # 标注类别名称

    # 因子信息列表（仅当映射器开启因子解析时初始化）
    factor_values_with_unit: List[List[str]] = [[] for _ in range(num_factors)] if need_parse_factors else []  # 因子值+单位
    factor_indices_list: List[List[int]] = [[] for _ in range(num_factors)] if need_parse_factors else []  # 因子编码

    # ------------------------------
    # 3. 按类别遍历，收集图片及（可选）因子信息
    # ------------------------------
    for class_name in valid_classes:
        # 构建当前类别图片文件夹路径
        class_img_dir = os.path.join(image_root_dir, class_name)
        if not os.path.exists(class_img_dir):
            continue  # 跳过映射器中存在但实际无文件夹的类别

        # 收集该类别下的有效图片（筛选支持的后缀，忽略大小写）
        image_extensions = ('.bmp', '.jpg', '.jpeg', '.png')
        class_images = [
            img for img in os.listdir(class_img_dir)
            if img.lower().endswith(image_extensions)
        ]
        if not class_images:
            continue  # 跳过无图片的类别

        # 图片自然排序（保证跨平台顺序一致性）
        class_images_sorted = sorted(class_images, key=natural_sort_key)
        img_count = len(class_images_sorted)

        # ------------------------------
        # 3.1 收集基础信息（批量添加）
        # ------------------------------
        class_image_paths = [os.path.join(class_img_dir, img) for img in class_images_sorted]
        class_target = mapper.get_label_from_class(class_name)  # 从映射器获取类别ID

        full_image_paths.extend(class_image_paths)
        targets.extend([class_target] * img_count)
        class_names.extend([class_name] * img_count)

        # ------------------------------
        # 3.2 收集因子信息（拼接“值+单位”）
        # ------------------------------
        if need_parse_factors:
            # 从映射器获取当前类别的因子原始值和编码
            factors = mapper.get_factors_from_class(class_name)
            factor_indices = mapper.get_indices_from_factors(factors)

            # 批量添加因子信息到列表（保持因子顺序一致性）
            for i in range(num_factors):
                factor_val = factors[i]
                factor_unit = mapper.factor_units[i]
                # 拼接逻辑：有单位则“值+单位”，无单位则保留原值（如“No”→“No”）
                val_with_unit = f"{factor_val}{factor_unit}" if factor_unit else factor_val
                factor_values_with_unit[i].extend([val_with_unit] * img_count)
                factor_indices_list[i].extend([factor_indices[i]] * img_count)

    # ------------------------------
    # 4. 校验数据完整性并构建DataFrame
    # ------------------------------
    if not full_image_paths:
        raise RuntimeError("❌ 未收集到任何有效图片！请检查:1.类别文件夹路径 2.图片后缀是否支持")

    # 基础DataFrame（必选列：图片路径→标注类别ID→标注类别名称）
    base_columns = {
        '图片路径': full_image_paths,
        '标注类别ID': targets,
        '标注类别名称': class_names
    }
    image_df = pd.DataFrame(base_columns)

    # ------------------------------
    # 核心修改：先加所有因子值列，再加所有因子编码列
    # ------------------------------
    if need_parse_factors:
        # 第一步：集中添加所有“因子值列”（按因子顺序：工况→Fault Location→Fault Size...）
        for i in range(num_factors):
            factor_col_name = mapper.factor_base_names[i]  # 列名：纯因子名（如“工况”）
            image_df[factor_col_name] = factor_values_with_unit[i]  # 列内容：因子值+单位（如“0HP”）

        # 第二步：集中添加所有“因子编码列”（按因子顺序：工况编码→Fault Location编码→Fault Size编码...）
        for i in range(num_factors):
            factor_code_col_name = f"{mapper.factor_base_names[i]}编码"  # 列名：纯因子名+编码（如“工况编码”）
            image_df[factor_code_col_name] = factor_indices_list[i]  # 列内容：因子编码（如0）

    return image_df, mapper


def create_csv(data, file_path):
    """
    根据给定的字典或列表生成CSV文件

    参数:
        data: 可以是列表（作为表头）或字典（键为表头,值为数据）
        file_path: 字符串,CSV文件的保存路径（包括文件名）
    """
    if isinstance(data, list):
        # 处理列表:仅作为表头创建空文件
        df = pd.DataFrame(columns=data)
    elif isinstance(data, dict):
        # 处理字典:键作为表头,值作为数据
        # 检查是否所有值都是列表且长度一致
        values = list(data.values())
        if all(isinstance(v, list) for v in values):
            # 确保所有列表长度相同
            lengths = set(len(v) for v in values)
            if len(lengths) <= 1:  # 允许所有空列表或长度一致的非空列表
                df = pd.DataFrame(data)
            else:
                raise ValueError("字典中所有值的列表长度必须一致")
        else:
            raise ValueError("字典的值必须是列表类型")
    else:
        raise TypeError("data必须是列表或字典类型")

    # 保存为CSV文件
    df.to_csv(file_path, index=False)


def append_metrics_to_csv(metrics, filename='training_metrics.csv'):
    """
    将一轮训练的指标数据按CSV表头顺序整理后追加到文件

    参数:
        metrics: 字典,包含当前轮次的指标数据
        filename: 保存指标的CSV文件名
    """
    # 检查文件是否存在
    if not os.path.exists(filename):
        raise FileNotFoundError(f"文件 {filename} 不存在,请先创建包含表头的CSV文件")

    # 读取CSV文件的表头（仅读取第一行）
    with open(filename, 'r') as f:
        header = f.readline().strip().split(',')

    # 检查metrics是否包含所有表头字段
    missing_keys = [key for key in header if key not in metrics]
    if missing_keys:
        raise ValueError(f"metrics缺少以下必要字段: {missing_keys}")

    # 按表头顺序重新整理字典
    ordered_metrics = {key: metrics[key] for key in header}

    # 转换为DataFrame并追加到CSV
    df = pd.DataFrame([ordered_metrics])
    df.to_csv(filename, mode='a', header=False, index=False)


def create_next_numbered_folder(parent_dir, prefix):
    """
    检查指定文件夹中以指定前缀+数字命名的子文件夹,创建缺失的最小数字对应的文件夹

    参数:
        parent_dir: 父文件夹路径
        prefix: 子文件夹的前缀（如"exp"、"test"等）

    返回:
        新创建的文件夹路径,如果创建失败则返回None
    """
    # 确保父文件夹存在
    if not os.path.exists(parent_dir):
        try:
            os.makedirs(parent_dir)
        except OSError as e:
            print(f"创建父文件夹失败: {e}")
            return None

    # 构建匹配指定前缀+数字格式的正则表达式
    # 转义前缀中的特殊字符,确保正则表达式正确匹配
    escaped_prefix = re.escape(prefix)
    pattern = re.compile(f'^{escaped_prefix}-(\\d+)$')

    # 收集所有符合条件的文件夹的数字
    numbers = []
    for item in os.listdir(parent_dir):
        item_path = os.path.join(parent_dir, item)
        if os.path.isdir(item_path):
            match = pattern.match(item)
            if match:
                try:
                    number = int(match.group(1))
                    numbers.append(number)
                except ValueError:
                    # 忽略数字部分无法转换为整数的文件夹
                    continue

    # 找到最小的缺失数字
    if not numbers:
        # 没有任何符合条件的文件夹,从1开始
        next_number = 1
    else:
        # 排序现有数字
        numbers.sort()
        # 检查从1开始的序列中第一个缺失的数字
        next_number = 1
        for num in numbers:
            if num > next_number:
                break
            next_number = num + 1

    # 创建新文件夹
    new_folder_name = f"{prefix}-{next_number}"
    new_folder_path = os.path.join(parent_dir, new_folder_name)

    try:
        os.makedirs(new_folder_path, exist_ok=False)  # 不覆盖现有文件夹
        return new_folder_path
    except OSError as e:
        print(f"创建文件夹失败: {e}")
        return None


def save_class_mean_features(encoding_path, csv_path, show_feature='故障工况', save_npy_path='.'):
    """
    计算每个类别的特征均值并分别保存为npy文件

    参数:
        encoding_path: 特征数组的npy文件路径（形状为 [样本数, 特征维度]）
        csv_path: 包含标签信息的CSV文件路径
        show_feature: 用于分类的特征列名（如'故障工况'）
        save_npy_path: 保存npy文件的目录路径
    """

    # 1. 加载特征数组和CSV标签数据
    # file_path = os.path.join(encoding_path, f'{show_feature}.npy')
    encoding_array = np.load(encoding_path, allow_pickle=True)

    df = pd.read_csv(csv_path)

    # 2. 验证数据有效性
    if len(encoding_array) != len(df):
        raise ValueError(f"特征样本数（{len(encoding_array)}）与CSV行数（{len(df)}）不匹配")

    if show_feature not in df.columns:
        raise ValueError(f"CSV文件中未找到'{show_feature}'列,请检查列名是否正确")

    # 3. 按类别计算特征均值并保存
    class_names = df[show_feature].unique().tolist()

    for cls in class_names:
        # 提取该类别的所有样本特征
        cls_mask = df[show_feature] == cls
        cls_feats = encoding_array[cls_mask]

        if len(cls_feats) == 0:
            continue

        # 计算特征均值（按特征维度求平均）
        cls_mean = np.mean(cls_feats, axis=0)

        # 生成保存路径（格式:show_feature_类别.npy）
        # 处理类别名中的特殊字符（如斜杠、空格等）
        safe_cls_name = str(cls).replace('/', '_').replace(' ', '_')
        file_name = f"{show_feature}_{safe_cls_name}.npy"
        save_path = os.path.join(save_npy_path, file_name)

        # 保存为npy文件
        np.save(save_path, cls_mean)


def concat_fault_features(type_path, degree_path, output_dir=None):
    """
    拼接Fault Location、程度特征,生成格式正确的文件名:
    - 仅当无有效数字时省略程度标识
    - 即使程度为0（如"0英寸"）也保留"0"
    - 格式:类型[-(程度)]（如No-0.npy、B-007.npy）
    """

    # 1. 提取故障类型标识（保留完整标识,过滤特殊字符）
    def extract_type_key(filename):
        base_name = os.path.splitext(os.path.basename(filename))[0]
        if "Fault Location" not in base_name:
            raise ValueError(f"文件需包含'Fault Location',输入为:{base_name}")
        # 保留字母/数字,过滤下划线、空格等特殊字符
        return re.sub(r'[^A-Za-z0-9]', '', base_name.split('_')[-1])

    # 2. 提取故障程度标识（只要有数字就保留，包括0；无有效数字则省略）
    def extract_degree_key(filename):
        base_name = os.path.splitext(os.path.basename(filename))[0]
        if "Fault Size" not in base_name:
            raise ValueError(f"文件需包含'Fault Size',输入为:{base_name}")
        degree_part = base_name.split('_')[-1]
        numbers = re.findall(r'\d+', degree_part)  # 提取所有数字序列
        # 只要能提取到数字（包括0、00等），就返回第一个数字序列
        if numbers:
            return numbers[0]
        return ''  # 无有效数字时返回空

    # 提取类型、程度关键标识
    type_key = extract_type_key(type_path)
    degree_key = extract_degree_key(degree_path)  # 有数字则保留（包括0），无数字则为空

    # 生成输出文件名（自动剔除空值部分,避免多余分隔符）
    parts = [type_key, degree_key]
    non_empty_parts = [part for part in parts if part]  # 过滤空的程度标识
    output_filename = "-".join(non_empty_parts) + ".npy"  # 如"No-0.npy"、"B-007.npy"

    # 确定输出路径（默认与Fault Location文件同目录下的"fault_combined"文件夹）
    if output_dir is None:
        type_dir = os.path.dirname(type_path)  # 取Fault Location文件的目录
        output_dir = os.path.join(type_dir, "fault_combined")
    os.makedirs(output_dir, exist_ok=True)  # 确保输出目录存在
    output_path = os.path.join(output_dir, output_filename)

    # 加载并拼接特征（类型特征 → 程度特征）
    try:
        # 加载一维特征数组
        type_feat = np.load(type_path, allow_pickle=True)
        degree_feat = np.load(degree_path, allow_pickle=True)
    except Exception as e:
        raise FileNotFoundError(f"特征文件加载失败: {str(e)}")

    # 验证特征维度（必须为一维数组,避免拼接异常）
    for feat, name in zip(
            [type_feat, degree_feat],
            ["Fault Location", "Fault Size"]
    ):
        if feat.ndim != 1:
            raise ValueError(f"{name}特征必须为一维数组,实际维度: {feat.ndim}")

    # 拼接特征（类型在前,程度在后）
    combined_feat = np.concatenate([type_feat, degree_feat], axis=0)
    # combined_feat = np.add(type_feat, degree_feat)
    np.save(output_path, combined_feat)


def write_list_to_file(str_list, file_path):
    """
    将字符串列表中的每个元素写入到txt文件，每个元素占一行

    参数:
        str_list: 字符串列表
        file_path: 要写入的文件路径
    """
    try:
        # 使用with语句打开文件，自动处理文件关闭
        with open(file_path, 'w', encoding='utf-8') as file:
            for item in str_list:
                # 确保每个元素都是字符串类型并添加换行符
                file.write(str(item) + '\n')
    except Exception as e:
        print(f"写入文件时发生错误: {e}")


def extract_class_features(csv_path, npy_base_dir, name, save_dir):
    """
    根据变量t（既是CSV的类别列名，也是NPY文件名的核心组成），从NPY特征文件中提取对应类别特征并保存

    参数说明：
    csv_path (str): CSV文件路径，需包含名为`t`的类别列（用于划分特征类别）
    npy_base_dir (str): NPY特征文件的基础目录（原代码中NPY路径为`{npy_base_dir}/{t}.npy`）
    name (str): 关键变量，同时承担两个角色：1. CSV中的类别列名；2. NPY文件名（不含后缀）
    save_dir (str, optional): 提取后特征的保存目录。

    返回值：
    dict: 键为类别名称，值为该类别特征文件的完整保存路径，便于后续追溯

    异常处理：
    - FileNotFoundError: CSV文件、NPY特征文件不存在时抛出
    - ValueError: t为空字符串、CSV缺少t列、NPY与CSV样本数不匹配时抛出
    - Exception: 捕获其他未知错误并提示
    """
    try:
        # 1. 基础参数校验（避免t为空或无效路径）
        save_dir_path = Path(save_dir)
        save_dir_path.mkdir(parents=True, exist_ok=True)  # 自动创建目录（含多级目录）

        # 3. 加载CSV文件并校验
        df = pd.read_csv(csv_path)

        features = np.load(npy_base_dir, allow_pickle=False)  # 禁止加载pickle对象，提升安全性
        # 5. 提取所有唯一类别并处理
        unique_classes = df[name].unique()
        class_save_paths = {}  # 存储类别-保存路径映射

        for idx, class_name in enumerate(unique_classes, 1):
            # 获取当前类别的样本索引（按t列的类别值筛选）
            class_indices = df[df[name] == class_name].index
            # 提取对应类别的特征（形状：[该类别样本数, 特征维度]）
            class_features = features[class_indices]
            # 构建保存路径（原代码命名格式：class_name.npy）
            save_filename = f"{class_name}.npy"
            save_full_path = str(save_dir_path / save_filename)

            # 保存特征文件
            np.save(save_full_path, class_features)
            # 记录保存路径
            class_save_paths[class_name] = save_full_path

    except FileNotFoundError as e:
        print(f"文件错误：{str(e)}")
        raise  # 重新抛出异常，便于调用方捕获处理
    except ValueError as e:
        print(f"数据有效性错误：{str(e)}")
        raise
    except Exception as e:
        print(f"未知错误：{str(e)}")
        raise

def zip_and_download(file_or_dir, output_filename='output.zip', compression_level=zipfile.ZIP_DEFLATED,
                     target_dir='/kaggle/working/'):
    """
    压缩文件/目录并根据环境提供下载方式
    """
    if not os.path.exists(file_or_dir):
        raise FileNotFoundError(f"源路径不存在: {file_or_dir}")

    original_dir = os.getcwd()
    output_path = os.path.join(target_dir, output_filename)

    try:
        os.chdir(target_dir)

        if not output_filename.endswith('.zip'):
            output_filename = f"{output_filename}.zip"

        with zipfile.ZipFile(output_filename, 'w',
                             compression=zipfile.ZIP_DEFLATED,
                             compresslevel=compression_level) as zipf:

            if os.path.isfile(file_or_dir):
                zipf.write(file_or_dir, os.path.basename(file_or_dir))
            else:
                for root, _, files in os.walk(file_or_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(file_or_dir))
                        zipf.write(file_path, arcname)

        # 检测是否在Jupyter环境中运行
        if 'IPKernelApp' in get_ipython().config:
            print("在Notebook中点击下方链接下载:")
            display(FileLink(output_filename))

        print(f"压缩完成！ZIP文件路径: {output_path}")
        print("在Kaggle中，您可以在右侧面板的Output标签中找到下载链接")

    except Exception as e:
        print(f"压缩失败: {str(e)}")
        return None
    finally:
        os.chdir(original_dir)