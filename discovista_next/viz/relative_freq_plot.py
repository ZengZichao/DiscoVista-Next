"""
相对频率可视化模块
==================

替代原 ``freqQuadVisualization.R`` (未包含在参考项目中但功能已从代码中推断)，
绘制四分体拓扑的相对频率图。
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


class RelativeFreqPlot:
    """相对频率可视化器。"""

    # ------------------------------------------------------------------
    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    # ------------------------------------------------------------------
    def plot_relative_freq(self, freq_file: str,
                            figure_size: Tuple[float, float] = (15, 10)) -> str:
        """绘制相对频率图。

        显示三种拓扑 (t1=主拓扑, t2/t3=备择拓扑) 在各关键分支附近的频率。

        Parameters
        ----------
        freq_file : str
            freqQuadCorrected.csv 文件路径。
            每行: node topology key type(t1/t2/t3)

        Returns
        -------
        str
            输出文件路径。
        """
        df = pd.read_csv(freq_file, sep="\t", header=None,
                          names=["node", "topology", "key", "type"])

        # 按 node 分组
        nodes = df["node"].unique()

        n_nodes = len(nodes)
        n_cols = 3
        n_rows = (n_nodes + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols,
                                  figsize=figure_size,
                                  constrained_layout=True)
        if n_rows == 1:
            axes = axes.reshape(1, -1) if n_cols > 1 else [axes]

        for idx, node in enumerate(nodes):
            row, col = idx // n_cols, idx % n_cols
            ax = axes[row][col] if n_rows > 1 else axes[col]

            sub = df[df["node"] == node]

            # 按拓扑类型分组
            t1 = sub[sub["type"] == "t1"]
            t2 = sub[sub["type"] == "t2"]
            t3 = sub[sub["type"] == "t3"]

            x_labels = range(len(t1))
            width = 0.6

            # 绘制三个拓扑的频率
            if len(t1) > 0:
                ax.bar(x_labels, t1.iloc[:, 1].astype(float).values,
                        width, color="red", alpha=0.7, label="t1 (main)")
            if len(t2) > 0:
                ax.bar(x_labels, t2.iloc[:, 1].astype(float).values,
                        width, color="blue", alpha=0.5, label="t2")
            if len(t3) > 0:
                ax.bar(x_labels, t3.iloc[:, 1].astype(float).values,
                        width, color="lightblue", alpha=0.5, label="t3")

            # 1/3 阈值线
            ax.axhline(y=1/3, color="black", linestyle="--", linewidth=0.8)

            ax.set_title(f"Branch {node}", fontsize=8)
            ax.set_xlabel("Quartet topology", fontsize=7)
            ax.set_ylabel("Frequency", fontsize=7)
            ax.legend(fontsize=6, loc="upper right")
            ax.tick_params(labelsize=6)

        # 隐藏多余的子图
        for idx in range(n_nodes, n_rows * n_cols):
            row, col = idx // n_cols, idx % n_cols
            ax = axes[row][col] if n_rows > 1 else axes[col]
            ax.set_visible(False)

        out_path = os.path.join(self.out_dir, "relativeFreq.pdf")
        _save_figure(fig, out_path)
        plt.close(fig)
        return out_path

    # ------------------------------------------------------------------
    def run(self, freq_file: str) -> None:
        """执行完整的相对频率可视化。"""
        self.plot_relative_freq(freq_file)
