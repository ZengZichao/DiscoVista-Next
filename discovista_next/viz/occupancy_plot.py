"""
占据率可视化模块
================

替代原 ``occupancy.R`` 的绘图部分，使用 matplotlib 绘制占据率折线图和热图。
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from typing import Tuple, Optional


def _save_figure(fig, out_path: str, **kwargs) -> str:
    """保存图形为 PDF 和 PNG 两种格式。"""
    fig.savefig(out_path, bbox_inches="tight", dpi=300, **kwargs)
    if out_path.endswith(".pdf"):
        png_path = out_path[:-4] + ".png"
    else:
        png_path = out_path + ".png"
    fig.savefig(png_path, bbox_inches="tight", dpi=150, **kwargs)
    print(f"Saved: {out_path}")
    print(f"Saved: {png_path}")
    return png_path


class OccupancyPlot:
    """占据率可视化器。"""

    # ------------------------------------------------------------------
    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    # ------------------------------------------------------------------
    def plot_occupancy_line(self, df: pd.DataFrame, max_g: int,
                            figure_size: Tuple[float, float] = (21, 10)) -> str:
        """绘制物种占据率折线图。

        Parameters
        ----------
        df : pd.DataFrame
            包含 ID, Taxon, occupancy 列的数据。
        max_g : int
            最大基因数。
        """
        fig, ax = plt.subplots(figsize=figure_size)

        ids = df["ID"].unique()
        colors = plt.cm.Paired(np.linspace(0, 1, len(ids)))

        for idx, id_val in enumerate(ids):
            sub = df[df["ID"] == id_val].copy()
            sub["occupancy_ratio"] = sub["occupancy"] / max_g
            # 按 occupancy_ratio 中位数排序 Taxon
            sub = sub.sort_values("occupancy_ratio")
            ax.plot(sub["Taxon"], sub["occupancy_ratio"],
                    label=id_val, color=colors[idx], linewidth=1)

        ax.set_xlabel("Taxon", fontsize=16)
        ax.set_ylabel("Occupancy", fontsize=24)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90, fontsize=8)
        ax.tick_params(axis="y", labelsize=16)
        ax.legend(loc="lower center", fontsize=12, ncol=min(5, len(ids)))
        ax.set_ylim(0, 1)

        out_path = os.path.join(self.out_dir, "occupancy.pdf")
        _save_figure(fig, out_path)
        plt.close(fig)
        return out_path

    # ------------------------------------------------------------------
    def plot_occupancy_clades(self, df: pd.DataFrame,
                              figure_size: Tuple[float, float] = (5, 3.5)) -> str:
        """绘制进化支占据率折线图。

        Parameters
        ----------
        df : pd.DataFrame
            包含 ID, Clade, clade_occupancy 列的数据。
        """
        fig, ax = plt.subplots(figsize=figure_size)

        ids = df["ID"].unique()
        colors = plt.cm.Paired(np.linspace(0, 1, len(ids)))

        for idx, id_val in enumerate(ids):
            sub = df[df["ID"] == id_val].copy()
            sub = sub.sort_values("clade_occupancy")
            ax.plot(sub["Clade"], sub["clade_occupancy"],
                    label=id_val, color=colors[idx], linewidth=1)

        ax.set_xlabel("Clades", fontsize=10)
        ax.set_ylabel("Percent", fontsize=10)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90,
                           fontsize=10, ha="right")
        ax.legend(loc="lower center", fontsize=8, ncol=min(3, len(ids)))
        ax.set_ylim(0, 1)

        out_path = os.path.join(self.out_dir, "occupancy_clades.pdf")
        _save_figure(fig, out_path)
        plt.close(fig)
        return out_path

    # ------------------------------------------------------------------
    def plot_occupancy_map(self, df: pd.DataFrame,
                           figure_size: Tuple[float, float] = (21, 6)) -> str:
        """绘制单一模型条件的占据率热图 (tile map)。

        Parameters
        ----------
        df : pd.DataFrame
            包含 GENE_ID, Taxon, Len 列的数据。
        """
        pivot = df.pivot_table(index="Taxon", columns="GENE_ID",
                               values="Len", aggfunc="sum", fill_value=0)
        # 归一化
        row_max = pivot.max(axis=1).replace(0, 1)
        pivot_norm = pivot.div(row_max, axis=0)

        fig, ax = plt.subplots(figsize=figure_size)
        cmap = mcolors.LinearSegmentedColormap.from_list(
            "occupancy", ["white", "#00740b"])
        im = ax.imshow(pivot_norm.values, aspect="auto", cmap=cmap)

        ax.set_xticks(range(len(pivot_norm.columns)))
        ax.set_xticklabels(pivot_norm.columns, rotation=90, fontsize=3)
        ax.set_yticks(range(len(pivot_norm.index)))
        ax.set_yticklabels(pivot_norm.index, fontsize=8)
        ax.set_xlabel("Gene ID")
        ax.set_ylabel("Taxon")

        out_path = os.path.join(self.out_dir, "occupancy_map.pdf")
        _save_figure(fig, out_path)
        plt.close(fig)
        return out_path

    # ------------------------------------------------------------------
    def run(self, species_df: pd.DataFrame, clades_df: pd.DataFrame,
            max_g: int, single_model_df: pd.DataFrame = None) -> None:
        """执行完整的占据率可视化。"""
        self.plot_occupancy_line(species_df, max_g)
        self.plot_occupancy_clades(clades_df)
        if single_model_df is not None and not single_model_df.empty:
            self.plot_occupancy_map(single_model_df)
