"""
分支统计可视化模块
==================

替代原 ``branchStat.R``，绘制分支支持值与分支长度的关系图和直方图。
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Tuple


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


class BranchStatPlot:
    """分支统计可视化器。"""

    # ------------------------------------------------------------------
    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    # ------------------------------------------------------------------
    def plot_histogram(self, branch_support_file: str,
                        figure_size: Tuple[float, float] = (30, 15)) -> str:
        """绘制 MLBS 分布直方图。

        Parameters
        ----------
        branch_support_file : str
            branchSupport.csv 文件路径。
            格式: DS model_condition support (空格分隔)
        """
        d1 = pd.read_csv(branch_support_file, sep=" ", header=None,
                          names=["V1", "V2", "V3"])

        ds_values = d1["V1"].unique()
        model_values = d1["V2"].unique()

        fig, axes = plt.subplots(len(ds_values), 1,
                                  figsize=figure_size,
                                  constrained_layout=True)
        if len(ds_values) == 1:
            axes = [axes]

        for ax, ds in zip(axes, ds_values):
            sub = d1[d1["V1"] == ds]
            for model in model_values:
                sub_m = sub[sub["V2"] == model]
                if not sub_m.empty:
                    ax.hist(sub_m["V3"], bins=range(0, 110, 10),
                            alpha=0.5, label=model, edgecolor="black",
                            linewidth=0.5)
            ax.set_title(ds, fontsize=12)
            ax.set_xlabel("MLBS", fontsize=12)
            ax.set_ylabel("Count", fontsize=12)
            ax.legend(fontsize=10)

        out_path = os.path.join(self.out_dir, "histogram_MLBS_distribution.pdf")
        _save_figure(fig, out_path)
        plt.close(fig)
        return out_path

    # ------------------------------------------------------------------
    def plot_avg_distance_vs_support(self, branch_stat_file: str,
                                      figure_size: Tuple[float, float] = (7, 4.5)) -> str:
        """绘制平均分类群距离 vs 平均支持值散点图。

        Parameters
        ----------
        branch_stat_file : str
            branchStats.csv 文件路径。
        """
        d = pd.read_csv(branch_stat_file, sep=" ", header=0)
        cdat = d.groupby(["DS", "model_condition"]).agg({
            "avgtaxonToTaxonBrLen": "mean",
            "maxtaxonToTaxonBrLen": "mean",
            "avgBrSupp": "mean",
        }).reset_index()

        ds_values = cdat["DS"].unique()
        model_values = cdat["model_condition"].unique()
        colors = plt.cm.Paired(np.linspace(0, 1, len(model_values)))
        color_map = dict(zip(model_values, colors))

        fig, axes = plt.subplots(1, len(ds_values),
                                  figsize=(figure_size[0] * len(ds_values),
                                           figure_size[1]),
                                  constrained_layout=True)
        if len(ds_values) == 1:
            axes = [axes]

        for ax, ds in zip(axes, ds_values):
            sub = cdat[cdat["DS"] == ds]
            for _, row in sub.iterrows():
                ax.scatter(row["avgtaxonToTaxonBrLen"], row["avgBrSupp"],
                            color=color_map.get(row["model_condition"], "gray"),
                            s=40, label=row["model_condition"])
            ax.set_xlabel("average taxa distance", fontsize=10)
            ax.set_ylabel("average bootstrap support", fontsize=10)
            ax.set_title(ds, fontsize=12)

        # 去重图例
        handles, labels = axes[0].get_legend_handles_labels()
        unique = dict(zip(labels, handles))
        fig.legend(unique.values(), unique.keys(),
                    loc="lower center", ncol=min(4, len(unique)),
                    fontsize=10)

        out_path = os.path.join(self.out_dir,
                                 "average_taxa_distance_vs_MLBS.pdf")
        _save_figure(fig, out_path)
        plt.close(fig)
        return out_path

    # ------------------------------------------------------------------
    def plot_max_distance_vs_support(self, branch_stat_file: str,
                                      figure_size: Tuple[float, float] = (7, 4.5)) -> str:
        """绘制最大分类群距离 vs 平均支持值散点图。"""
        d = pd.read_csv(branch_stat_file, sep=" ", header=0)
        cdat = d.groupby(["DS", "model_condition"]).agg({
            "maxtaxonToTaxonBrLen": "mean",
            "avgBrSupp": "mean",
        }).reset_index()

        ds_values = cdat["DS"].unique()
        model_values = cdat["model_condition"].unique()
        colors = plt.cm.Paired(np.linspace(0, 1, len(model_values)))
        color_map = dict(zip(model_values, colors))

        fig, axes = plt.subplots(1, len(ds_values),
                                  figsize=(figure_size[0] * len(ds_values),
                                           figure_size[1]),
                                  constrained_layout=True)
        if len(ds_values) == 1:
            axes = [axes]

        for ax, ds in zip(axes, ds_values):
            sub = cdat[cdat["DS"] == ds]
            for _, row in sub.iterrows():
                ax.scatter(row["maxtaxonToTaxonBrLen"], row["avgBrSupp"],
                            color=color_map.get(row["model_condition"], "gray"),
                            s=40, label=row["model_condition"])
            ax.set_xlabel("average maximum taxa distance", fontsize=10)
            ax.set_ylabel("average bootstrap support", fontsize=10)
            ax.set_title(ds, fontsize=12)

        handles, labels = axes[0].get_legend_handles_labels()
        unique = dict(zip(labels, handles))
        fig.legend(unique.values(), unique.keys(),
                    loc="lower center", ncol=min(4, len(unique)),
                    fontsize=10)

        out_path = os.path.join(self.out_dir,
                                 "maximum_taxa_distance_vs_MLBS.pdf")
        _save_figure(fig, out_path)
        plt.close(fig)
        return out_path

    # ------------------------------------------------------------------
    def run(self, branch_stat_file: str, branch_support_file: str) -> None:
        """执行完整的分支统计可视化。"""
        self.plot_histogram(branch_support_file)
        self.plot_avg_distance_vs_support(branch_stat_file)
        self.plot_max_distance_vs_support(branch_stat_file)
