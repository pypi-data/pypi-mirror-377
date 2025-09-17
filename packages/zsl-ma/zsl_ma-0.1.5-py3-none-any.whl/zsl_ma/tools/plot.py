# import os
#
# import numpy as np
# import pandas as pd
# import seaborn as sns
# from matplotlib import pyplot as plt, font_manager
# from sklearn.decomposition import PCA
# from sklearn.manifold import TSNE
# from sklearn.metrics import confusion_matrix
#
#
# def _get_times_new_roman_config():
#     """辅助函数：获取Times New Roman字体配置，失败则返回空字典（用默认字体）"""
#     target_font = "Times New Roman"
#     font_config = {}
#     try:
#         # 检查系统是否存在目标字体（用'family'参数匹配FontProperties）
#         font_props = font_manager.FontProperties(family=target_font)
#         font_path = font_manager.findfont(font_props)
#         # 验证字体路径是否包含目标字体特征（避免误匹配）
#         if target_font.lower() in font_path.lower() or "times" in font_path.lower():
#             font_config = {"family": target_font}  # 键为'family'，适配FontProperties
#             print(f"✅ 检测到Times New Roman字体，已应用")
#     except Exception as e:
#         # 捕获字体不存在、路径查找失败等异常，降级为默认字体
#         print(f"⚠️ 未检测到Times New Roman字体（错误：{str(e)[:50]}），使用系统默认字体")
#     return font_config
#
#
# def visualize_mean_features(encoding_path, csv_path, show_feature='标注类别名称',
#                             save_fig_path='combined_vis.jpg'):
#     """
#     修复size_max参数错误,将类别特征平均值作为虚拟样本加入原始特征一起降维可视化
#     额外修复：图例title_fontsize与title_fontproperties参数冲突，统一用FontProperties配置标题字体
#     """
#     # 1. 初始化字体配置（优先Times New Roman）
#     font_config = _get_times_new_roman_config()
#     text_font = font_config.get('family') if font_config else None
#
#     # 2. 加载数据
#     encoding_array = np.load(encoding_path, allow_pickle=True)
#     df = pd.read_csv(csv_path)
#
#     # 验证数据有效性
#     if len(encoding_array) != len(df):
#         raise ValueError("特征样本数与CSV行数不匹配")
#     for col in [show_feature, '图片路径']:
#         if col not in df.columns:
#             raise ValueError(f"CSV缺少必要列:{col}")
#
#     # 3. 计算每个类别的特征平均值（作为"虚拟样本"）
#     class_names = df[show_feature].unique().tolist()
#     n_classes = len(class_names)
#     print(f"计算 {n_classes} 个类别的特征平均值,作为虚拟样本加入原始特征...")
#
#     mean_feats_list = []
#     mean_labels = []
#     for cls in class_names:
#         cls_feats = encoding_array[df[show_feature] == cls]
#         cls_mean = np.mean(cls_feats, axis=0)
#         mean_feats_list.append(cls_mean)
#         mean_labels.append(cls)
#
#     mean_feats_array = np.array(mean_feats_list)
#     combined_feats = np.vstack([encoding_array, mean_feats_array])
#
#     # 4. 准备合并后的标签数据
#     original_labels = df[show_feature].tolist()
#     original_types = ['原始样本'] * len(original_labels)
#     original_names = df['图片路径'].apply(lambda x: x.split('/')[-1]).tolist()
#
#     mean_types = ['均值样本'] * n_classes
#     mean_names = [f"{cls}_均值" for cls in class_names]
#
#     combined_labels = original_labels + mean_labels
#     combined_types = original_types + mean_types
#     combined_names = original_names + mean_names
#
#     # 5. TSNE降维
#     print("对合并后的特征（原始样本+均值样本）进行TSNE降维...")
#     tsne = TSNE(n_components=2, max_iter=20000, random_state=42)
#     combined_tsne_2d = tsne.fit_transform(combined_feats)
#
#     # 6. 准备可视化数据
#     vis_df = pd.DataFrame({
#         'X': combined_tsne_2d[:, 0],
#         'Y': combined_tsne_2d[:, 1],
#         show_feature: combined_labels,
#         '样本类型': combined_types,
#         '名称': combined_names,
#         '尺寸数值': [1 if t == '原始样本' else 5 for t in combined_types]
#     })
#
#     # 7. 绘制静态图（修复图例参数冲突）
#     plt.figure(figsize=(14, 12), facecolor='white')
#     palette = sns.hls_palette(n_classes)
#     cls_color_map = {cls: palette[i] for i, cls in enumerate(class_names)}
#
#     # 绘制原始样本
#     original_mask = vis_df['样本类型'] == '原始样本'
#     for cls in class_names:
#         cls_mask = original_mask & (vis_df[show_feature] == cls)
#         plt.scatter(
#             vis_df.loc[cls_mask, 'X'],
#             vis_df.loc[cls_mask, 'Y'],
#             color=cls_color_map[cls],
#             alpha=0.4,
#             s=30,
#             marker='o',
#             label=cls
#         )
#
#     # 绘制均值样本+类别名称标注
#     mean_mask = vis_df['样本类型'] == '均值样本'
#     for cls in class_names:
#         cls_mean_mask = mean_mask & (vis_df[show_feature] == cls)
#         # 均值样本散点
#         plt.scatter(
#             vis_df.loc[cls_mean_mask, 'X'],
#             vis_df.loc[cls_mean_mask, 'Y'],
#             color=cls_color_map[cls],
#             s=400,
#             marker='*',
#             edgecolors='black',
#             linewidths=2,
#             zorder=10
#         )
#         # 类别名称文本（显式指定fontfamily）
#         plt.text(
#             vis_df.loc[cls_mean_mask, 'X'].values[0] + 3.0,
#             vis_df.loc[cls_mean_mask, 'Y'].values[0],
#             cls,
#             fontsize=12,
#             fontweight='bold',
#             color=cls_color_map[cls],
#             bbox=dict(facecolor='white', edgecolor='gray', pad=3, alpha=0.8),
#             fontfamily=text_font
#         )
#
#     # 图例（修复参数冲突：去掉title_fontsize，将标题字体大小合并到title_fontproperties）
#     plt.legend(
#         title=show_feature,
#         fontsize=10,  # 图例项的字体大小（非标题）
#         bbox_to_anchor=(1.05, 1),
#         # 关键修复：用title_fontproperties同时配置标题字体家族和大小，避免与title_fontsize冲突
#         title_fontproperties=font_manager.FontProperties(
#             family=text_font,
#             size=12  # 原title_fontsize=12的功能迁移到这里
#         ) if text_font else font_manager.FontProperties(size=12),
#         # 图例项的字体配置
#         prop=font_manager.FontProperties(family=text_font, size=10) if text_font else None
#     )
#
#     # 轴刻度（显式传递fontfamily）
#     plt.xticks([], fontfamily=text_font)
#     plt.yticks([], fontfamily=text_font)
#
#     plt.tight_layout()
#     plt.savefig(save_fig_path, dpi=500, bbox_inches='tight')
#     print(f"静态图已保存至: {save_fig_path}")
#     plt.close()
#
#
# def npy_dim_reduction_visualization(npy_dir, dim_method="pca", save_path=None):
#     """
#     对文件夹内的任意一维npy文件进行降维可视化（维度不固定，需所有样本维度一致）
#     """
#     # 1. 初始化字体配置（优先Times New Roman）
#     font_config = _get_times_new_roman_config()
#     text_font = font_config.get('family') if font_config else None
#
#     # 2. 读取所有npy文件
#     npy_files = [f for f in os.listdir(npy_dir) if f.endswith(".npy")]
#     if len(npy_files) == 0:
#         raise FileNotFoundError(f"文件夹 {npy_dir} 中未找到npy文件")
#     if len(npy_files) < 2:
#         raise ValueError(f"至少需要2个npy文件才能进行降维，当前仅找到 {len(npy_files)} 个")
#
#     data_list = []
#     file_labels = []
#     target_dim = None
#
#     for filename in npy_files:
#         file_path = os.path.join(npy_dir, filename)
#         try:
#             data = np.load(file_path, allow_pickle=True).squeeze()
#             if data.ndim != 1:
#                 raise ValueError(f"非一维数据：{filename} 维度为 {data.shape}（需一维数组）")
#
#             if target_dim is None:
#                 target_dim = len(data)
#                 print(f"检测到数据维度：{target_dim} 维（以 {filename} 为基准）")
#             else:
#                 if len(data) != target_dim:
#                     raise ValueError(
#                         f"维度不一致：{filename} 为 {len(data)} 维，需与基准维度 {target_dim} 一致"
#                     )
#
#             data_list.append(data)
#             file_labels.append(os.path.splitext(filename)[0])
#
#         except Exception as e:
#             raise RuntimeError(f"处理文件 {filename} 失败：{str(e)}")
#
#     data_matrix = np.array(data_list)
#     sample_num, feat_dim = data_matrix.shape
#     print(f"数据加载完成：共 {sample_num} 个样本，每个样本 {feat_dim} 维")
#
#     # 3. 降维处理
#     if dim_method.lower() == "pca":
#         reducer = PCA(n_components=2, random_state=42)
#         reduced_data = reducer.fit_transform(data_matrix)
#         title_suffix = f"PCA降维可视化（原维度：{feat_dim}）"
#         explained_var = reducer.explained_variance_ratio_
#         print(
#             f"PCA降维结果：维度1解释 {explained_var[0]:.3f} 方差，维度2解释 {explained_var[1]:.3f} 方差（累计：{np.sum(explained_var):.3f}）")
#
#     elif dim_method.lower() == "tsne":
#         perplexity = min(max(2, sample_num // 4), sample_num - 1)
#         reducer = TSNE(
#             n_components=2,
#             random_state=42,
#             perplexity=perplexity,
#             init="pca"
#         )
#         reduced_data = reducer.fit_transform(data_matrix)
#         title_suffix = f"t-SNE降维可视化（原维度：{feat_dim}，perplexity={perplexity}）"
#         print(f"t-SNE降维完成（自动设置perplexity={perplexity}，适配 {sample_num} 个样本）")
#
#     else:
#         raise ValueError(f"不支持的降维方法 {dim_method}，仅可选'pca'或'tsne'")
#
#     # 4. 可视化
#     fig, ax = plt.subplots(figsize=(10, 8))
#
#     scatter = ax.scatter(
#         reduced_data[:, 0],
#         reduced_data[:, 1],
#         c=range(sample_num),
#         cmap="tab10" if sample_num <= 10 else "viridis",
#         s=120 if sample_num <= 15 else 80,
#         alpha=0.8,
#         edgecolors="black",
#         linewidth=1
#     )
#
#     # 样本标签注释（显式传递fontfamily）
#     for i, (x, y, label) in enumerate(zip(reduced_data[:, 0], reduced_data[:, 1], file_labels)):
#         ax.annotate(
#             label,
#             xy=(x, y),
#             xytext=(6, 6) if sample_num <= 10 else (4, 4),
#             textcoords="offset points",
#             fontsize=10 if sample_num <= 10 else 8,
#             bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
#             fontfamily=text_font
#         )
#
#     # 轴标签（显式传递fontfamily）
#     ax.set_xlabel("dim 1", fontsize=12, fontfamily=text_font)
#     ax.set_ylabel("dim 2", fontsize=12, fontfamily=text_font)
#     ax.grid(True, alpha=0.3)
#
#     # 颜色条标签（显式传递fontfamily）
#     cbar = plt.colorbar(scatter, ax=ax)
#     cbar.set_label("sample index", fontsize=10, fontfamily=text_font)
#     cbar.set_ticks(range(sample_num))
#
#     plt.tight_layout()
#
#     if save_path is not None:
#         os.makedirs(os.path.dirname(save_path), exist_ok=True)
#         plt.savefig(save_path, dpi=300, bbox_inches="tight")
#         print(f"图片已保存至：{save_path}")
#     else:
#         plt.show()
#
#
# def plot_confusion_matrix(
#         y_true,
#         y_pred,
#         classes,
#         save_path='confusion_matrix.jpg',
#         normalize=False,
#         title='Confusion Matrix',
#         cmap=plt.cm.Blues
# ):
#     """
#     功能整合版混淆矩阵工具：
#     1. 计算混淆矩阵（支持原始计数/按真实类别归一化）；
#     2. 数值在格子中水平+垂直双居中，避免偏上；
#     3. 优先使用Times New Roman字体（系统存在则应用，否则保留默认）；
#     4. 自适应画布尺寸，无多余空白且标签完整显示。
#     """
#     # 1. 初始化字体配置（复用统一逻辑）
#     font_config = _get_times_new_roman_config()
#     text_font = font_config.get('family') if font_config else None
#
#     # 2. 计算混淆矩阵
#     cm = confusion_matrix(
#         y_true=y_true,
#         y_pred=y_pred,
#         labels=np.arange(len(classes))
#     )
#
#     # 3. 绘制混淆矩阵
#     base_size = 0.9 if len(classes) <= 6 else (0.7 if len(classes) <= 12 else 0.55)
#     fig = plt.figure(figsize=(len(classes) * base_size, len(classes) * base_size * 0.8))
#
#     if normalize:
#         cm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
#         print(f"📊 混淆矩阵已归一化（按真实类别）")
#
#     im = plt.imshow(cm, interpolation="nearest", cmap=cmap)
#     plt.colorbar(im)
#
#     # 标题（显式传递fontfamily）
#     if title:
#         plt.title(title, fontsize=12, fontfamily=text_font, pad=15)
#
#     # 轴刻度与类别标签（显式传递fontfamily）
#     tick_marks = np.arange(len(classes))
#     plt.xticks(
#         tick_marks, classes,
#         rotation=45 if len(classes) <= 11 else 90,
#         ha="center", fontsize=10, fontfamily=text_font
#     )
#     plt.yticks(tick_marks, classes, fontsize=10, fontfamily=text_font)
#
#     # 单元格数值（显式传递fontfamily）
#     fmt = ".2f" if normalize else "d"
#     thresh = cm.max() / 2.
#     for i, j in np.ndindex(cm.shape):
#         plt.text(
#             j, i, format(cm[i, j], fmt),
#             horizontalalignment="center",
#             verticalalignment="center",
#             color="white" if cm[i, j] > thresh else "black",
#             fontsize=10, fontfamily=text_font
#         )
#
#     # 轴标签（显式传递fontfamily）
#     plt.ylabel("True Label", fontsize=11, fontfamily=text_font, labelpad=10)
#     plt.xlabel("Predicted Label", fontsize=11, fontfamily=text_font, labelpad=10)
#
#     plt.subplots_adjust(left=0.12, right=0.95, bottom=0.15 if len(classes) <= 8 else 0.2, top=0.88)
#     plt.tight_layout()
#
#     plt.savefig(save_path, dpi=1000, bbox_inches="tight", bbox_extra_artists=[im])
#     plt.close(fig)
#     print(f"💾 混淆矩阵已保存至：{save_path}")

import os

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt, font_manager
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import confusion_matrix


plt.rcParams["font.family"] = 'Times New Roman'
plt.rcParams['axes.unicode_minus'] = False
def visualize_mean_features(encoding_path, csv_path, show_feature='标注类别名称',
                            save_fig_path='combined_vis.jpg'):
    """
    修复size_max参数错误,将类别特征平均值作为虚拟样本加入原始特征一起降维可视化
    Fix size_max parameter error, add category feature averages as virtual samples to original features for dimensionality reduction visualization
    """
    # 1. 加载数据
    # 1. Load data
    encoding_array = np.load(encoding_path, allow_pickle=True)
    df = pd.read_csv(csv_path)

    # 验证数据有效性
    # Verify data validity
    if len(encoding_array) != len(df):
        raise ValueError(
            "特征样本数与CSV行数不匹配")  # The number of feature samples does not match the number of CSV rows
    for col in [show_feature, '图片路径']:
        if col not in df.columns:
            raise ValueError(f"CSV缺少必要列:{col}")  # CSV lacks necessary column: {col}

    # 2. 计算每个类别的特征平均值（作为"虚拟样本"）
    # 2. Calculate feature averages for each category (as "virtual samples")
    class_names = df[show_feature].unique().tolist()
    n_classes = len(class_names)
    print(
        f"计算 {n_classes} 个类别的特征平均值,作为虚拟样本加入原始特征...")  # Calculating feature averages for {n_classes} categories to add as virtual samples to original features...

    # 按类别分组求均值
    # Calculate averages by category group
    mean_feats_list = []
    mean_labels = []
    for cls in class_names:
        cls_feats = encoding_array[df[show_feature] == cls]
        cls_mean = np.mean(cls_feats, axis=0)
        mean_feats_list.append(cls_mean)
        mean_labels.append(cls)

    # 转换为数组并合并
    # Convert to array and merge
    mean_feats_array = np.array(mean_feats_list)
    combined_feats = np.vstack(
        [encoding_array, mean_feats_array])  # 合并原始特征与均值特征 (Merge original features with mean features)

    # 3. 准备合并后的标签数据
    # 3. Prepare merged label data
    original_labels = df[show_feature].tolist()
    original_types = ['原始样本'] * len(original_labels)  # '原始样本' corresponds to "Original Sample"
    original_names = df['图片路径'].apply(lambda x: x.split('/')[-1]).tolist()  # '图片路径' corresponds to "Image Path"

    mean_types = ['均值样本'] * n_classes  # '均值样本' corresponds to "Mean Sample"
    mean_names = [f"{cls}_均值" for cls in class_names]  # '_均值' corresponds to "_mean"

    combined_labels = original_labels + mean_labels
    combined_types = original_types + mean_types
    combined_names = original_names + mean_names

    # 4. 对合并后的特征进行TSNE降维
    # 4. Perform TSNE dimensionality reduction on combined features
    print(
        "对合并后的特征（原始样本+均值样本）进行TSNE降维...")  # Performing TSNE dimensionality reduction on combined features (original samples + mean samples)...
    tsne = TSNE(n_components=2, max_iter=20000,
                random_state=42)  # 注意:sklearn 1.5+用max_iter替代n_iter (Note: sklearn 1.5+ uses max_iter instead of n_iter)
    combined_tsne_2d = tsne.fit_transform(combined_feats)

    # 5. 准备可视化数据（新增尺寸数值列）
    # 5. Prepare visualization data (add size value column)
    vis_df = pd.DataFrame({
        'X': combined_tsne_2d[:, 0],
        'Y': combined_tsne_2d[:, 1],
        show_feature: combined_labels,
        '样本类型': combined_types,  # '样本类型' corresponds to "Sample Type"
        '名称': combined_names,  # '名称' corresponds to "Name"
        '尺寸数值': [1 if t == '原始样本' else 5 for t in combined_types]
        # 原始样本=1,均值样本=5 (Original sample=1, Mean sample=5)
    })

    # 6. 绘制静态图
    # 6. Draw static graph
    plt.figure(figsize=(14, 12), facecolor='white')
    palette = sns.hls_palette(n_classes)
    cls_color_map = {cls: palette[i] for i, cls in enumerate(class_names)}

    # 绘制原始样本
    # Draw original samples
    original_mask = vis_df['样本类型'] == '原始样本'
    for cls in class_names:
        cls_mask = original_mask & (vis_df[show_feature] == cls)
        plt.scatter(
            vis_df.loc[cls_mask, 'X'],
            vis_df.loc[cls_mask, 'Y'],
            color=cls_color_map[cls],
            alpha=0.4,
            s=30,
            marker='o',
            label=cls
        )

    # 绘制均值样本
    # Draw mean samples
    mean_mask = vis_df['样本类型'] == '均值样本'
    for i, cls in enumerate(class_names):
        cls_mean_mask = mean_mask & (vis_df[show_feature] == cls)
        plt.scatter(
            vis_df.loc[cls_mean_mask, 'X'],
            vis_df.loc[cls_mean_mask, 'Y'],
            color=cls_color_map[cls],
            s=400,
            marker='*',
            edgecolors='black',
            linewidths=2,
            zorder=10
        )

        # 在均值样本旁添加类别名称
        # Add category name next to mean sample
        plt.text(
            vis_df.loc[cls_mean_mask, 'X'].values[0] + 3.0,  # x轴偏移一点,避免重叠 (Offset x-axis slightly to avoid overlap)
            vis_df.loc[cls_mean_mask, 'Y'].values[0],  # y轴对齐 (Align with y-axis)
            cls,  # 类别名称 (Category name)
            fontsize=12,
            fontweight='bold',
            color=cls_color_map[cls],
            bbox=dict(facecolor='white', edgecolor='gray', pad=3, alpha=0.8)
            # 白色背景框增强可读性 (White background box enhances readability)
        )

    # 将图例标题改为英文，原中文意思：标注类别名称
    # Change legend title to English, original Chinese meaning: "标注类别名称" (Annotation Category Name)
    plt.legend(title=show_feature, fontsize=10, title_fontsize=12, bbox_to_anchor=(1.05, 1))
    plt.xticks([])
    plt.yticks([])
    # 移除图片标题（按照要求不绘制标题）
    # Remove image title (do not draw title as required)
    plt.tight_layout()
    plt.savefig(save_fig_path, dpi=500, bbox_inches='tight')
    print(f"静态图已保存至: {save_fig_path}")  # Static image saved to: {save_fig_path}
    plt.close()


def npy_dim_reduction_visualization(npy_dir, dim_method="pca", save_path=None):
    """
    对文件夹内的任意一维npy文件进行降维可视化（维度不固定，需所有样本维度一致）

    参数:
        npy_dir: npy文件所在文件夹路径
        dim_method: 降维方法，可选"pca"（默认）或"tsne"
        save_path: 图片保存路径（如None则不保存，仅显示）
    """
    # 1. 读取所有npy文件，动态适配维度
    npy_files = [f for f in os.listdir(npy_dir) if f.endswith(".npy")]
    if len(npy_files) == 0:
        raise FileNotFoundError(f"文件夹 {npy_dir} 中未找到npy文件")
    if len(npy_files) < 2:
        raise ValueError(f"至少需要2个npy文件才能进行降维，当前仅找到 {len(npy_files)} 个")

    data_list = []
    file_labels = []
    target_dim = None

    for filename in npy_files:
        file_path = os.path.join(npy_dir, filename)
        try:
            data = np.load(file_path, allow_pickle=True).squeeze()
            if data.ndim != 1:
                raise ValueError(f"非一维数据：{filename} 维度为 {data.shape}（需一维数组）")

            if target_dim is None:
                target_dim = len(data)
                print(f"检测到数据维度：{target_dim} 维（以 {filename} 为基准）")
            else:
                if len(data) != target_dim:
                    raise ValueError(
                        f"维度不一致：{filename} 为 {len(data)} 维，需与基准维度 {target_dim} 一致"
                    )

            data_list.append(data)
            file_labels.append(os.path.splitext(filename)[0])

        except Exception as e:
            raise RuntimeError(f"处理文件 {filename} 失败：{str(e)}")

    data_matrix = np.array(data_list)
    sample_num, feat_dim = data_matrix.shape  # 这里定义了feat_dim（每个样本的维度）
    print(f"数据加载完成：共 {sample_num} 个样本，每个样本 {feat_dim} 维")

    # 2. 降维处理
    if dim_method.lower() == "pca":
        reducer = PCA(n_components=2, random_state=42)
        reduced_data = reducer.fit_transform(data_matrix)
        title_suffix = f"PCA降维可视化（原维度：{feat_dim}）"
        explained_var = reducer.explained_variance_ratio_
        print(
            f"PCA降维结果：维度1解释 {explained_var[0]:.3f} 方差，维度2解释 {explained_var[1]:.3f} 方差（累计：{np.sum(explained_var):.3f}）")

    elif dim_method.lower() == "tsne":
        perplexity = min(max(2, sample_num // 4), sample_num - 1)
        reducer = TSNE(
            n_components=2,
            random_state=42,
            perplexity=perplexity,
            init="pca"
        )
        reduced_data = reducer.fit_transform(data_matrix)
        title_suffix = f"t-SNE降维可视化（原维度：{feat_dim}，perplexity={perplexity}）"
        print(f"t-SNE降维完成（自动设置perplexity={perplexity}，适配 {sample_num} 个样本）")

    else:
        raise ValueError(f"不支持的降维方法 {dim_method}，仅可选'pca'或'tsne'")

    # 3. 可视化（修正变量名错误）
    # plt.rcParams["font.sans-serif"] = ["SimHei", "WenQuanYi Zen Hei"]
    # plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(10, 8))

    scatter = ax.scatter(
        reduced_data[:, 0],
        reduced_data[:, 1],
        c=range(sample_num),
        cmap="tab10" if sample_num <= 10 else "viridis",
        s=120 if sample_num <= 15 else 80,
        alpha=0.8,
        edgecolors="black",
        linewidth=1
    )

    for i, (x, y, label) in enumerate(zip(reduced_data[:, 0], reduced_data[:, 1], file_labels)):
        ax.annotate(
            label,
            xy=(x, y),
            xytext=(6, 6) if sample_num <= 10 else (4, 4),
            textcoords="offset points",
            fontsize=10 if sample_num <= 10 else 8,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8)
        )

    # 关键修正：将n_dim改为feat_dim（已定义的变量）
    # ax.set_title(f"{sample_num}个{feat_dim}维npy文件-{title_suffix}", fontsize=14, fontweight="bold")
    ax.set_xlabel("dim 1", fontsize=12)
    ax.set_ylabel("dim 2", fontsize=12)
    ax.grid(True, alpha=0.3)

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("smple idex", fontsize=10)
    cbar.set_ticks(range(sample_num))

    plt.tight_layout()

    if save_path is not None:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"图片已保存至：{save_path}")
    else:
        plt.show()


def plot_confusion_matrix(
        y_true,
        y_pred,
        classes,
        save_path='confusion_matrix.jpg',
        normalize=False,
        title='Confusion Matrix',
        cmap=plt.cm.Blues
):
    """
    功能整合版混淆矩阵工具：
    1. 计算混淆矩阵（支持原始计数/按真实类别归一化）；
    2. 数值在格子中水平+垂直双居中，避免偏上；
    3. 优先使用Times New Roman字体（系统存在则应用，否则保留默认）；
    4. 自适应画布尺寸，无多余空白且标签完整显示。

    参数：
        y_true: 真实标签（array-like，形状(n_samples,)）
        y_pred: 预测标签（array-like，与y_true形状一致）
        classes: 类别名称列表（list，与标签索引一一对应）
        save_path: 图像保存路径（默认'confusion_matrix.jpg'）
        normalize: 是否按真实类别（行）归一化（默认False）
        title: 混淆矩阵标题（默认'Confusion Matrix'）
        cmap: 颜色映射（默认plt.cm.Blues，可换'viridis'等）

    返回：
        np.ndarray: 计算后的混淆矩阵（原始/归一化）
    """

    # -------------------------- 2. 计算混淆矩阵（确保类别顺序与classes一致） --------------------------
    cm = confusion_matrix(
        y_true=y_true,
        y_pred=y_pred,
        labels=np.arange(len(classes))  # 标签索引匹配classes长度
    )

    # -------------------------- 3. 绘制混淆矩阵（整合所有优化） --------------------------
    # 自适应画布：类别越多，单位尺寸越小，避免整体过大/过小
    base_size = 0.9 if len(classes) <= 6 else (0.7 if len(classes) <= 12 else 0.55)
    fig = plt.figure(figsize=(len(classes) * base_size, len(classes) * base_size * 0.8))

    # 归一化处理（按真实类别行求和归一化）
    if normalize:
        cm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
        print(f"📊 混淆矩阵已归一化（按真实类别）")

    # 绘制矩阵主体
    im = plt.imshow(cm, interpolation="nearest", cmap=cmap)
    plt.colorbar(im)  # 颜色条（辅助理解数值与颜色对应）

    # 标题：应用字体配置，控制字体大小
    if title:
        plt.title(title, fontsize=12, pad=15)

    # 刻度与类别标签：旋转X轴标签避免重叠，应用字体
    tick_marks = np.arange(len(classes))
    plt.xticks(
        tick_marks, classes,
        rotation=45 if len(classes) <= 11 else 90,  # 类别多则竖排标签
        ha="center", fontsize=10
    )
    plt.yticks(tick_marks, classes, fontsize=10)

    # 单元格数值：水平+垂直双居中，按背景色适配文字色
    fmt = ".2f" if normalize else "d"  # 归一化显示2位小数，原始显示整数
    thresh = cm.max() / 2.  # 阈值：区分深色/浅色背景
    for i, j in np.ndindex(cm.shape):
        plt.text(
            j, i, format(cm[i, j], fmt),
            horizontalalignment="center",  # 水平居中
            verticalalignment="center",  # 垂直居中（解决偏上问题）
            color="white" if cm[i, j] > thresh else "black",
            fontsize=10  # 数值字体稍小，避免拥挤
        )

    # 轴标签：应用字体，调整位置避免截断
    plt.ylabel("True Label", fontsize=11, labelpad=10)
    plt.xlabel("Predicted Label", fontsize=11, labelpad=10)

    # 精准调整边距：确保无多余空白，标签完整
    plt.subplots_adjust(left=0.12, right=0.95, bottom=0.15 if len(classes) <= 8 else 0.2, top=0.88)
    plt.tight_layout()

    # 保存高分辨率图像（自动裁剪边缘空白）
    plt.savefig(save_path, dpi=500, bbox_inches="tight", bbox_extra_artists=[im])
    plt.close(fig)
    print(f"💾 混淆矩阵已保存至：{save_path}")
