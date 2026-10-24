"""
系统发育树可视化模块
====================

替代原 ``plotTree.R``，使用 matplotlib 绘制 Newick 树的多种视图：
矩形树、无根树、径向树和分支图。
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Optional

import dendropy


def _save_figure(fig, out_path: str, **kwargs) -> str:
    """保存图形为 PDF 和 PNG 两种格式。"""
    fig.savefig(out_path, bbox_inches="tight", dpi=300, **kwargs)
    if out_path.endswith(".pdf"):
        png_path = out_path[:-4] + ".png"
    else:
        png_path = out_path + ".png"
    fig.savefig(png_path, bbox_inches="tight", dpi=150, **kwargs)
    return png_path


class TreePlot:
    """系统发育树可视化器。"""

    # ------------------------------------------------------------------
    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    # ------------------------------------------------------------------
    @staticmethod
    def _collect_tree_data(tree: dendropy.Tree):
        """递归收集树结构数据用于绘图。"""
        nodes_data = []

        def _recurse(node, x=0, y=0, y_counter=[0]):
            if node.is_leaf():
                y_counter[0] += 1
                y = y_counter[0]
                nodes_data.append({
                    "label": node.taxon.label if node.taxon else "",
                    "x": x, "y": y, "is_leaf": True,
                    "length": node.edge.length,
                })
                return y

            child_ys = []
            for child in node.child_nodes():
                edge_len = child.edge.length if child.edge.length else 0
                cy = _recurse(child, x + edge_len, y, y_counter)
                child_ys.append(cy)

            y = sum(child_ys) / len(child_ys) if child_ys else y_counter[0]
            nodes_data.append({
                "label": node.label or "",
                "x": x, "y": y, "is_leaf": False,
                "length": node.edge.length,
            })
            return y

        _recurse(tree.seed_node)
        return nodes_data

    # ------------------------------------------------------------------
    def plot_tree_rectangular(self, tree: dendropy.Tree, ax=None,
                               show_support: bool = True) -> None:
        """绘制矩形系统发育树。"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 8))

        def _draw(node, x=0, y=[0], depth=0):
            if node.is_leaf():
                y[0] += 1
                label = node.taxon.label if node.taxon else ""
                ax.annotate(label, (x, y[0]), fontsize=4,
                            ha="left", va="center")
                return y[0]

            child_ys = []
            for child in node.child_nodes():
                edge_len = child.edge.length if child.edge.length else 1
                cy = _draw(child, x + edge_len, y, depth + 1)
                # 画水平线
                ax.plot([x, x + edge_len], [cy, cy], "orange", linewidth=2)
                child_ys.append(cy)

            mid_y = sum(child_ys) / len(child_ys) if child_ys else 0
            # 画垂直线连接子节点
            if len(child_ys) >= 2:
                ax.plot([x, x], [min(child_ys), max(child_ys)],
                         "orange", linewidth=2)
            if show_support and node.label:
                ax.text(x, mid_y, str(node.label), fontsize=4,
                        ha="center", va="bottom",
                        bbox=dict(boxstyle="round,pad=0.1",
                                   facecolor="black", edgecolor="none"),
                        color="white")
            return mid_y

        _draw(tree.seed_node)
        ax.set_axis_off()

    # ------------------------------------------------------------------
    def plot_tree_radial(self, tree: dendropy.Tree, ax=None) -> None:
        """绘制径向系统发育树。"""
        import math
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))

        leaves = list(tree.leaf_node_iter())
        n_leaves = len(leaves)
        angle_map = {}
        for i, leaf in enumerate(leaves):
            angle_map[leaf] = 2 * math.pi * i / n_leaves

        def _draw(node):
            if node.is_leaf():
                angle = angle_map.get(node, 0)
                radius = 0
                # 计算到根的距离
                n = node
                r = 0
                while n.parent_node is not None:
                    if n.edge.length:
                        r += n.edge.length
                    n = n.parent_node
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                label = node.taxon.label if node.taxon else ""
                ax.annotate(label, (x, y), fontsize=3)
                return angle, r

            child_data = []
            for child in node.child_nodes():
                child_data.append(_draw(child))

            if not child_data:
                return 0, 0

            avg_angle = sum(d[0] for d in child_data) / len(child_data)
            n = node
            r = 0
            while n.parent_node is not None:
                if n.edge.length:
                    r += n.edge.length
                n = n.parent_node
            x = r * math.cos(avg_angle)
            y = r * math.sin(avg_angle)
            return avg_angle, r

        _draw(tree.seed_node)
        ax.set_aspect("equal")
        ax.set_axis_off()

    # ------------------------------------------------------------------
    def plot_tree(self, tree_file: str) -> str:
        """绘制树的多种视图到单个 PDF。

        Parameters
        ----------
        tree_file : str
            Newick 格式树文件路径。

        Returns
        -------
        str
            输出文件路径。
        """
        tree = dendropy.Tree.get(path=tree_file, schema="newick")
        d = os.path.dirname(os.path.abspath(tree_file))

        from matplotlib.backends.backend_pdf import PdfPages

        out_path = os.path.join(self.out_dir, "tree.pdf")
        with PdfPages(out_path) as pdf:
            # 矩形树
            fig, ax = plt.subplots(figsize=(12, 8))
            self.plot_tree_rectangular(tree, ax)
            ax.set_title("Rectangular Tree", fontsize=14)
            pdf.savefig(fig, bbox_inches="tight")
            png_path1 = os.path.join(self.out_dir, "tree_rectangular.png")
            fig.savefig(png_path1, bbox_inches="tight", dpi=150)
            plt.close(fig)

            # 径向树
            fig, ax = plt.subplots(figsize=(10, 10))
            self.plot_tree_radial(tree, ax)
            ax.set_title("Radial Tree", fontsize=14)
            pdf.savefig(fig, bbox_inches="tight")
            png_path2 = os.path.join(self.out_dir, "tree_radial.png")
            fig.savefig(png_path2, bbox_inches="tight", dpi=150)
            plt.close(fig)

            # 无根树
            fig, ax = plt.subplots(figsize=(10, 10))
            self.plot_tree_radial(tree, ax)
            ax.set_title("Unrooted Tree", fontsize=14)
            pdf.savefig(fig, bbox_inches="tight")
            png_path3 = os.path.join(self.out_dir, "tree_unrooted.png")
            fig.savefig(png_path3, bbox_inches="tight", dpi=150)
            plt.close(fig)

        print(f"Saved: {out_path}")
        print(f"Saved: {png_path1}")
        print(f"Saved: {png_path2}")
        print(f"Saved: {png_path3}")
        return out_path
