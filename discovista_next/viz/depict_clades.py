"""
进化支可视化模块
================

替代原 ``main_depict_clades.R`` 和 ``depict_clades.R`` 的全部绘图功能。
使用 matplotlib + seaborn 替代 R 的 ggplot2，生成物种树和基因树的
不一致性热图、条形图和直方图。
"""

import os
import re
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap


def _save_figure(fig, out_path: str, **kwargs) -> str:
    """保存图形为 PDF 和 PNG 两种格式。

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        要保存的图形。
    out_path : str
        输出文件路径（.pdf 后缀）。

    Returns
    -------
    str
        PNG 文件路径。
    """
    fig.savefig(out_path, bbox_inches="tight", dpi=300, **kwargs)
    if out_path.endswith(".pdf"):
        png_path = out_path[:-4] + ".png"
    else:
        png_path = out_path + ".png"
    fig.savefig(png_path, bbox_inches="tight", dpi=150, **kwargs)
    print(f"Saved: {out_path}")
    print(f"Saved: {png_path}")
    return png_path


class DepictClades:
    """进化支不一致性可视化器。

    读取 CladeAnalyzer 生成的结果文件，绘制：
    - 热图 (block diagram)：物种树/基因树中各进化支的支持状态
    - 带阴影的热图 (block-shades)：按支持值着色
    - 堆叠条形图：基因树中各进化支的分类比例
    - 直方图：自展支持分布
    """

    # 物种树颜色方案
    SPECIES_COLORS = {
        "Strong Support": "#0073b6ff",
        "Weak Support": "#00b5ecff",
        "Compatible (Weak Rejection)": "#f5e526ff",
        "Strong Rejection": "#f35e00ff",
        "Missing": "#808080",
    }

    # 基因树颜色方案
    GENE_COLORS = {
        "Strongly Supported": "#326478",
        "Weakly Supported": "#64a0fa",
        "Weakly Reject": "#fff0aa",
        "Strongly Reject": "#e6191a",
        "Missing": "#c0c0c0",
    }

    # 物种树分类映射 (missing=0)
    SPECIES_RENAME = {
        "IS_MONO-IS_MONO": "Strong Support",
        "IS_MONO-CAN_MONO": "Weak Support",
        "CAN_MONO-CAN_MONO": "Compatible (Weak Rejection)",
        "NOT_MONO-CAN_MONO": "Compatible (Weak Rejection)",
        "NOT_MONO-NOT_MONO": "Strong Rejection",
        "IS_MONO_INCOMPLETE-CAN_MONO": "Missing",
        "IS_MONO_INCOMPLETE-IS_MONO_INCOMPLETE": "Missing",
        "NOT_MONO-CAN_MONO_INCOMPLETE": "Missing",
        "NO_CLADE-NO_CLADE": "Missing",
        "CAN_MONO_INCOMPLETE-CAN_MONO_INCOMPLETE": "Missing",
        "IS_MONO_INCOMPLETE-CAN_MONO_INCOMPLETE": "Missing",
        "COMP_MISSING-COMP_MISSING": "Missing",
    }

    # 物种树分类映射 (missing=1)
    SPECIES_RENAME_MS = {
        "IS_MONO-IS_MONO": "Strong Support",
        "IS_MONO-CAN_MONO": "Weak Support",
        "CAN_MONO-CAN_MONO": "Compatible (Weak Rejection)",
        "NOT_MONO-CAN_MONO": "Compatible (Weak Rejection)",
        "NOT_MONO-NOT_MONO": "Strong Rejection",
        "IS_MONO_INCOMPLETE-CAN_MONO": "Weak Support",
        "IS_MONO_INCOMPLETE-IS_MONO_INCOMPLETE": "Strong Support",
        "NOT_MONO-CAN_MONO_INCOMPLETE": "Compatible (Weak Rejection)",
        "NO_CLADE-NO_CLADE": "Missing",
        "CAN_MONO_INCOMPLETE-CAN_MONO_INCOMPLETE": "Compatible (Weak Rejection)",
        "IS_MONO_INCOMPLETE-CAN_MONO_INCOMPLETE": "Weak Support",
        "COMP_MISSING-COMP_MISSING": "Missing",
    }

    # 基因树分类映射
    GENE_RENAME = {
        "IS_MONO-IS_MONO": "Strongly Supported",
        "IS_MONO_INCOMPLETE-IS_MONO_INCOMPLETE": "Strongly Supported",
        "IS_MONO-CAN_MONO": "Weakly Supported",
        "IS_MONO_INCOMPLETE-CAN_MONO_INCOMPLETE": "Weakly Supported",
        "NO_CLADE-NO_CLADE": "Missing",
        "COMP_MISSING-COMP_MISSING": "Missing",
        "CAN_MONO-CAN_MONO": "Weakly Reject",
        "CAN_MONO_INCOMPLETE-CAN_MONO_INCOMPLETE": "Weakly Reject",
        "NOT_MONO-CAN_MONO": "Weakly Reject",
        "NOT_MONO-CAN_MONO_INCOMPLETE": "Weakly Reject",
        "NOT_MONO-NOT_MONO": "Strongly Reject",
    }

    # ------------------------------------------------------------------
    def __init__(self, out_dir: str, is_species_tree: bool = True,
                 missing_flag: int = 0):
        self.out_dir = out_dir
        self.is_species_tree = is_species_tree
        self.missing_flag = missing_flag
        os.makedirs(out_dir, exist_ok=True)

        if is_species_tree:
            self.colors = self.SPECIES_COLORS
            self.rename_map = (self.SPECIES_RENAME_MS if missing_flag == 1
                               else self.SPECIES_RENAME)
        else:
            self.colors = self.GENE_COLORS
            self.rename_map = self.GENE_RENAME

    # ------------------------------------------------------------------
    def read_data(self, file_all: str, file_hs: str,
                  clade_order: List[str] = None,
                  new_clades: pd.DataFrame = None,
                  new_models: pd.DataFrame = None) -> dict:
        """读取分析结果文件并处理数据。

        Returns
        -------
        dict
            包含 y (分类数据)、countes.melted (计数数据)、raw.all (原始数据)。
        """
        raw_all = pd.read_csv(file_all, sep="\t")
        raw_hs = pd.read_csv(file_hs, sep="\t")

        # 确保 BOOT 为数值
        raw_all["BOOT"] = pd.to_numeric(raw_all["BOOT"], errors="coerce")

        # 取高支持结果中需要的列
        # 表头顺序（见 core/analyzer.py）：ID  DS  MONO  BOOT  CLADE  BRANCHLEN
        # 因此 [0, 1, 2, 4] 取到的是 ID, DS, MONO, CLADE
        raw_hs = raw_hs.iloc[:, [0, 1, 2, 4]]

        # 合并
        merged = raw_all[["ID", "DS", "CLADE", "MONO", "BOOT"]].copy()
        # LOCAL PATCH 20261024-1
        # 这里要取的是收缩树（高支持阈值）的单系状态 MONO，落在第 2 列。
        # 原实现取第 3 列，拿到的是 CLADE 名，Classification 于是拼成
        # "IS_MONO-Zygnematophyceae" 之类的非法组合，在 rename_map 中查不到
        # 而被全部 fillna("Missing")，比例图随之崩溃。
        merged["MONO.75"] = raw_hs.iloc[:, 2].values

        # 分类
        merged["Classification"] = merged["MONO"].astype(str) + "-" + \
            merged["MONO.75"].astype(str)
        merged["Classification"] = merged["Classification"].map(self.rename_map)
        merged["Classification"] = merged["Classification"].fillna("Missing")

        # 确定进化支排序
        if clade_order is None:
            mono_clades = raw_all[raw_all["MONO"].isin(
                ["IS_MONO", "IS_MONO_INCOMPLETE"])]
            clade_order = mono_clades["CLADE"].value_counts().index.tolist()

        merged["CLADE"] = pd.Categorical(merged["CLADE"],
                                          categories=clade_order,
                                          ordered=True)

        # 重命名进化支
        if new_clades is not None:
            old_orders = new_clades.iloc[0].tolist()
            modified = new_clades.iloc[1].tolist()
            mapping = dict(zip(old_orders, modified))
            merged["CLADE"] = merged["CLADE"].map(
                lambda x: mapping.get(str(x), str(x)))
            merged["CLADE"] = pd.Categorical(merged["CLADE"],
                                              categories=list(reversed(modified)),
                                              ordered=True)
            raw_all["CLADE"] = raw_all["CLADE"].map(
                lambda x: mapping.get(str(x), str(x)))

        # 重命名模型条件
        if new_models is not None:
            old_orders = new_models.iloc[0].tolist()
            modified = new_models.iloc[1].tolist()
            mapping = dict(zip(old_orders, modified))
            merged["ID"] = merged["ID"].map(lambda x: mapping.get(str(x), str(x)))
            raw_all["ID"] = raw_all["ID"].map(
                lambda x: mapping.get(str(x), str(x)))

        # 计算计数
        counts = (merged.groupby(["MONO", "MONO.75", "CLADE", "DS"])
                  .size().reset_index(name="value"))
        counts["Classification"] = (counts["MONO"].astype(str) + "-" +
                                     counts["MONO.75"].astype(str)).map(
                                        self.rename_map).fillna("Missing")
        counts_agg = (counts.groupby(["Classification", "CLADE", "DS"])
                      .size().reset_index(name="value"))
        counts_agg = counts_agg[counts_agg["value"] != 0]

        return {
            "y": merged,
            "counts_melted": counts_agg,
            "raw_all": raw_all,
        }

    # ------------------------------------------------------------------
    def plot_block(self, data: dict, figure_size: Tuple[float, float] = (10.5, 12),
                   page: int = 1) -> None:
        """绘制物种树不一致性热图。

        Parameters
        ----------
        data : dict
            read_data 返回的字典。
        figure_size : tuple
            图形尺寸 (宽, 高)。
        page : int
            页面类型: 1=完整, 2=仅有支持的, 3=强支持的。
        """
        y = data["y"]
        ds_values = y["DS"].unique()

        for ds in ds_values:
            y_ds = y[y["DS"] == ds]
            pivot = pd.crosstab(y_ds["ID"], y_ds["CLADE"],
                                values=y_ds["Classification"],
                                aggfunc="first")

            fig, ax = plt.subplots(figsize=figure_size)
            self._draw_heatmap(ax, pivot, y_ds)

            out_path = os.path.join(self.out_dir, f"{ds}.block.pdf")
            _save_figure(fig, out_path)
            plt.close(fig)

    # ------------------------------------------------------------------
    def _draw_heatmap(self, ax, pivot, y_ds):
        """绘制分类热图。"""
        classifications = list(self.colors.keys())
        color_list = [self.colors[c] for c in classifications]

        # 构建数值矩阵
        unique_clades = pivot.columns.tolist()
        unique_ids = pivot.index.tolist()
        n_clades = len(unique_clades)
        n_ids = len(unique_ids)

        matrix = np.zeros((n_clades, n_ids, 3))
        for i, clade in enumerate(unique_clades):
            for j, id_val in enumerate(unique_ids):
                val = pivot.loc[id_val, clade] if clade in pivot.columns else "Missing"
                if pd.isna(val):
                    val = "Missing"
                color = self.colors.get(val, "#c0c0c0")
                matrix[i, j] = self._hex_to_rgb(color)

        ax.imshow(matrix, aspect="auto")
        ax.set_xticks(range(n_ids))
        ax.set_xticklabels(unique_ids, rotation=90, fontsize=8)
        ax.set_yticks(range(n_clades))
        ax.set_yticklabels(unique_clades, fontsize=8)
        ax.set_xlabel("")
        ax.set_ylabel("")

        # 图例
        patches = [mpatches.Patch(color=self.colors[c], label=c)
                   for c in classifications if c in y_ds["Classification"].values]
        ax.legend(handles=patches, loc="upper center",
                   bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=7)

    # ------------------------------------------------------------------
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple:
        """将十六进制颜色转换为 RGB 元组 (0-1)。"""
        if not hex_color or not hex_color.startswith("#"):
            # Fallback for non-hex color names (e.g. R color names)
            return (0.5, 0.5, 0.5)
        hex_color = hex_color[1:]
        # 处理 8 位 hex (如 #0073b6ff)
        if len(hex_color) == 8:
            hex_color = hex_color[:6]
        if len(hex_color) != 6:
            return (0.5, 0.5, 0.5)
        try:
            r = int(hex_color[0:2], 16) / 255
            g = int(hex_color[2:4], 16) / 255
            b = int(hex_color[4:6], 16) / 255
            return (r, g, b)
        except ValueError:
            return (0.5, 0.5, 0.5)

    # ------------------------------------------------------------------
    def plot_block_shades(self, data: dict,
                          figure_size: Tuple[float, float] = (10.5, 12)) -> None:
        """绘制带阴影渐变的热图（按支持值着色）。"""
        y = data["y"]
        raw_all = data["raw_all"]
        ds_values = y["DS"].unique()

        for ds in ds_values:
            # 准备数据
            if self.missing_flag:
                db = raw_all[raw_all["MONO"].isin(
                    ["IS_MONO", "IS_MONO_INCOMPLETE"])]
            else:
                db = raw_all[raw_all["MONO"] == "IS_MONO"]

            dbc = y[y["Classification"] == "Compatible (Weak Rejection)"].copy()
            dbn = y[y["Classification"] == "Strong Rejection"].copy()
            dbc["BOOT"] = -50
            dbn["BOOT"] = -100

            cols = ["ID", "CLADE", "BOOT"]
            db2 = pd.concat([
                dbn[cols] if not dbn.empty else pd.DataFrame(columns=cols),
                dbc[cols] if not dbc.empty else pd.DataFrame(columns=cols),
                db[cols] if not db.empty else pd.DataFrame(columns=cols)
            ])

            # 确保 BOOT 列为数值类型，避免 concat 后变为 object dtype
            db2["BOOT"] = pd.to_numeric(db2["BOOT"], errors="coerce")

            pivot = db2.pivot_table(index="CLADE", columns="ID",
                                     values="BOOT", aggfunc="first")

            # 确保 pivot 值为 float 类型（NaN 表示缺失数据）
            pivot = pivot.astype(float)

            fig, ax = plt.subplots(figsize=figure_size)

            # 自定义渐变色
            colors_list = ["#257070", "#459090", "#599590", "#69a1a0",
                           "#DDEEFF", "#ec7f98", "#c84060"]
            cmap = LinearSegmentedColormap.from_list("custom", colors_list)
            im = ax.imshow(pivot.values, aspect="auto", cmap=cmap,
                            vmin=-100, vmax=100)
            ax.set_xticks(range(len(pivot.columns)))
            ax.set_xticklabels(pivot.columns, rotation=90, fontsize=8)
            ax.set_yticks(range(len(pivot.index)))
            ax.set_yticklabels(pivot.index, fontsize=8)
            plt.colorbar(im, ax=ax, fraction=0.02, pad=0.02)

            out_path = os.path.join(self.out_dir, f"{ds}.block-shades.pdf")
            _save_figure(fig, out_path)
            plt.close(fig)

    # ------------------------------------------------------------------
    def plot_bargraphs(self, data: dict,
                      figure_size: Tuple[float, float] = (15, 19)) -> None:
        """绘制基因树条形图（计数）。"""
        counts = data["counts_melted"]
        ds_values = counts["DS"].unique()

        fig, axes = plt.subplots(len(ds_values), 1,
                                  figsize=figure_size,
                                  constrained_layout=True)
        if len(ds_values) == 1:
            axes = [axes]

        for ax, ds in zip(axes, ds_values):
            sub = counts[counts["DS"] == ds]
            pivot = sub.pivot_table(index="CLADE", columns="Classification",
                                     values="value", aggfunc="sum",
                                     fill_value=0)
            for col in self.colors:
                if col not in pivot.columns:
                    pivot[col] = 0
            pivot = pivot[list(self.colors.keys())]

            pivot.plot(kind="bar", stacked=True, ax=ax,
                        color=[self.colors[c] for c in pivot.columns],
                        edgecolor="black", linewidth=0.5)
            ax.set_title(ds, fontsize=10)
            ax.set_xlabel("")
            ax.set_ylabel("Number of Gene Trees", fontsize=10)
            ax.legend(fontsize=8, loc="upper right")
            ax.tick_params(axis="x", rotation=90, labelsize=8)

        out_path = os.path.join(self.out_dir, "Monophyletic_Bargraphs.pdf")
        _save_figure(fig, out_path)
        plt.close(fig)

    # ------------------------------------------------------------------
    def plot_bargraphs_proportion(self, data: dict,
                                  figure_size: Tuple[float, float] = (15, 19)) -> None:
        """绘制基因树比例条形图。"""
        counts = data["counts_melted"]
        counts = counts[counts["Classification"] != "Missing"]
        ds_values = counts["DS"].unique()

        fig, axes = plt.subplots(len(ds_values), 1,
                                  figsize=figure_size,
                                  constrained_layout=True)
        if len(ds_values) == 1:
            axes = [axes]

        for ax, ds in zip(axes, ds_values):
            sub = counts[counts["DS"] == ds]
            pivot = sub.pivot_table(index="CLADE", columns="Classification",
                                     values="value", aggfunc="sum",
                                     fill_value=0)
            # 归一化为比例
            pivot = pivot.div(pivot.sum(axis=1), axis=0).fillna(0)
            for col in self.colors:
                if col not in pivot.columns:
                    pivot[col] = 0
            pivot = pivot[list(self.colors.keys())]

            pivot.plot(kind="bar", stacked=True, ax=ax,
                        color=[self.colors[c] for c in pivot.columns],
                        edgecolor="black", linewidth=0.5)
            ax.set_title(ds, fontsize=10)
            ax.set_xlabel("")
            ax.set_ylabel("Proportion of relevant gene trees", fontsize=10)
            ax.legend(fontsize=8, loc="upper right")
            ax.tick_params(axis="x", rotation=90, labelsize=8)

        out_path = os.path.join(self.out_dir, "Monophyletic_Bargraphs_Porportion.pdf")
        _save_figure(fig, out_path)
        plt.close(fig)

    # ------------------------------------------------------------------
    def plot_histograms(self, data: dict,
                        figure_size: Tuple[float, float] = (18, 18)) -> None:
        """绘制自展支持值分布直方图。"""
        raw_all = data["raw_all"]
        ds_values = raw_all["DS"].unique()

        fig, axes = plt.subplots(len(ds_values), 1,
                                  figsize=figure_size,
                                  constrained_layout=True)
        if len(ds_values) == 1:
            axes = [axes]

        for ax, ds in zip(axes, ds_values):
            sub = raw_all[(raw_all["MONO"].isin(["IS_MONO", "IS_MONO_INCOMPLETE"]))
                          & (raw_all["DS"] == ds)
                          & (raw_all["BOOT"].notna())]
            if sub.empty:
                ax.set_title(f"No data for {ds}")
                continue

            for clade in sub["CLADE"].unique():
                ax.hist(sub[sub["CLADE"] == clade]["BOOT"], bins=20,
                        alpha=0.5, label=clade)
            ax.set_title(f"Distribution of Support ({ds})", fontsize=10)
            ax.set_xlabel("Bootstrap Support")
            ax.set_ylabel("Frequency")
            ax.legend(fontsize=6, loc="upper right")

        out_path = os.path.join(self.out_dir, "Monophyletic_Bootstrap_Support_2.pdf")
        _save_figure(fig, out_path)
        plt.close(fig)
