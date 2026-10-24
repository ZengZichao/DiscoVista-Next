"""
GC 含量可视化模块
=================

替代原 ``plot.gc.R``，使用 matplotlib 绘制 GC 含量散点图和箱线图。
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
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


class GCPlot:
    """GC 含量可视化器。"""

    # ------------------------------------------------------------------
    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    # ------------------------------------------------------------------
    def plot_gc_point(self, gc_file: str,
                      figure_size: Tuple[float, float] = (12, 5)) -> str:
        """绘制 GC 含量散点图。

        Parameters
        ----------
        gc_file : str
            gc-stat.csv 文件路径。
        figure_size : tuple
            图形尺寸。

        Returns
        -------
        str
            输出文件路径。
        """
        f = pd.read_csv(gc_file, sep=" ")

        # 计算各密码子位置的 GC 含量
        f["ALL_GC"] = f["G_C"] + f["C_C"]
        f["C1_GC"] = f["c1_G_C"] + f["c1_C_C"]
        f["C2_GC"] = f["c2_G_C"] + f["c2_C_C"]
        f["C3_GC"] = f["c3_G_C"] + f["c3_C_C"]

        # 按物种聚合
        agg = f.groupby("SEQUENCE")[["ALL_GC", "C1_GC", "C2_GC", "C3_GC"]].mean()

        fig, ax = plt.subplots(figsize=figure_size)

        positions = ["ALL_GC", "C1_GC", "C2_GC", "C3_GC"]
        labels = ["All", "Position 1", "Position 2", "Position 3"]
        colors = ["red", "pink", "lightblue", "darkblue"]

        for pos, label, color in zip(positions, labels, colors):
            sorted_agg = agg.sort_values(pos)
            ax.scatter(range(len(sorted_agg)), sorted_agg[pos],
                       label=label, color=color, s=15, alpha=0.7)

        ax.set_xticks(range(len(agg)))
        ax.set_xticklabels(agg.index, rotation=90, fontsize=3)
        ax.set_xlabel("")
        ax.set_ylabel("GC content")
        ax.legend(loc="upper right", fontsize=8)
        ax.set_title("GC Content by Codon Position")

        out_path = os.path.join(self.out_dir, "pTpP_GC_point.pdf")
        _save_figure(fig, out_path)
        plt.close(fig)
        return out_path

    # ------------------------------------------------------------------
    def plot_gc_boxplot(self, gc_file: str,
                        figure_size: Tuple[float, float] = (12, 5)) -> str:
        """绘制 GC 含量箱线图。

        Parameters
        ----------
        gc_file : str
            gc-stat.csv 文件路径。

        Returns
        -------
        str
            输出文件路径。
        """
        f = pd.read_csv(gc_file, sep=" ")

        f["ALL_GC"] = f["G_C"] + f["C_C"]
        f["C1_GC"] = f["c1_G_C"] + f["c1_C_C"]
        f["C2_GC"] = f["c2_G_C"] + f["c2_C_C"]
        f["C3_GC"] = f["c3_G_C"] + f["c3_C_C"]

        melted = f.melt(id_vars=["GENE", "SEQUENCE", "TAXON"],
                         value_vars=["ALL_GC", "C1_GC", "C2_GC", "C3_GC"],
                         var_name="variable", value_name="GC")
        melted["variable"] = melted["variable"].map({
            "ALL_GC": "All", "C1_GC": "Position 1",
            "C2_GC": "Position 2", "C3_GC": "Position 3"})

        fig, axes = plt.subplots(4, 1, figsize=figure_size,
                                  constrained_layout=True, sharex=True)
        unique_sequences = melted["SEQUENCE"].unique()
        for ax, pos in zip(axes, ["All", "Position 1", "Position 2", "Position 3"]):
            sub = melted[melted["variable"] == pos]
            box_data = [sub[sub["SEQUENCE"] == s]["GC"].values
                        for s in unique_sequences]
            bp = ax.boxplot(box_data, flierprops=dict(marker=".",
                         markersize=3, alpha=0.1))
            ax.set_ylabel("GC content", fontsize=9)
            ax.set_title(pos, fontsize=10)
            ax.set_xticks(range(1, len(unique_sequences) + 1))

        axes[-1].set_xticklabels(unique_sequences,
                                  rotation=90, fontsize=3)
        axes[-1].set_xlabel("")

        out_path = os.path.join(self.out_dir, "pTpP_GC_boxplot.pdf")
        _save_figure(fig, out_path)
        plt.close(fig)
        return out_path

    # ------------------------------------------------------------------
    def run(self, gc_file: str) -> None:
        """执行完整的 GC 含量可视化。"""
        self.plot_gc_point(gc_file)
        self.plot_gc_boxplot(gc_file)
