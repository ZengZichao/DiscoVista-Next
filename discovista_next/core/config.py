"""
配置与选项处理模块
==================

替代原 ``reader.py`` 中的 ``Opt`` 类，负责解析命令行参数、验证输入、
确定文件搜索模式以及准备输出目录。

原作者使用 Python 2 的 ``optparse``，本模块改用 ``argparse``。
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Optional, List, Tuple


@dataclass
class Options:
    """封装 DiscoVista 运行所需的全部配置参数。

    Attributes
    ----------
    path : str
        数据目录的绝对路径。
    mode : int
        分析模式（0-5），详见 ``discovista_next`` 包常量。
    annotation : str
        注释文件路径（模式 3、5 需要）。
    clades : str
        进化支定义文件路径（模式 0、1 需要）。
    root : str
        根定义文件路径（模式 4 需要）。
    threshold : float
        自展支持阈值（模式 0、1 需要）。
    label : str
        输出目录路径。
    model_cond : Optional[str]
        占据率分析中指定单一模型条件。
    new_model : Optional[str]
        模型条件重排文件。
    new_order : Optional[str]
        进化支重排文件。
    missing : int
        缺失数据处理标志（1 = 部分缺失视为完整）。
    style : int
        颜色样式集编号（保留接口，当前未使用）。
    outg : str
        相对频率分析中指定的外群名称。
    names : str
        从注释文件自动生成的物种名称文件路径。
    search : Optional[str]
        原始文件 glob 模式。
    search_thr : Optional[str]
        收缩后文件 glob 模式。
    search_rooted : Optional[str]
        重根后文件 glob 模式。
    search_thr_rooted : Optional[str]
        收缩+重根后文件 glob 模式。
    """

    path: str = ""
    mode: int = -1
    annotation: str = ""
    clades: str = ""
    root: str = ""
    threshold: float = -1.0
    label: str = ""
    model_cond: Optional[str] = None
    new_model: Optional[str] = None
    new_order: Optional[str] = None
    missing: int = 0
    style: int = 0
    outg: str = ""
    names: str = ""
    search: Optional[str] = None
    search_thr: Optional[str] = None
    search_rooted: Optional[str] = None
    search_thr_rooted: Optional[str] = None

    # ------------------------------------------------------------------
    # 工厂方法
    # ------------------------------------------------------------------
    @classmethod
    def from_args(cls, argv: Optional[List[str]] = None) -> "Options":
        """从命令行参数构建 Options 对象。

        Parameters
        ----------
        argv : list[str] or None
            命令行参数列表。为 None 时使用 ``sys.argv``。
        """
        parser = cls._build_parser()
        ns = parser.parse_args(argv)
        return cls._from_namespace(parser, ns)

    @staticmethod
    def _build_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="discoVista",
            description=(
                "DiscoVista-Next: 系统发育不一致性可视化与分析工具\n"
                "DiscoVista-Next: Phylogenetic discordance visualization & analysis"
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "-a", "--annotation", dest="annotation", default=None,
            help="注释文件路径 / The annotation file",
        )
        parser.add_argument(
            "-c", "--clades", dest="clades", default=None,
            help="进化支定义文件路径 / Path to the clade definition file",
        )
        parser.add_argument(
            "-m", "--mode", dest="mode", default=None,
            help=(
                "分析模式 / Analysis mode: "
                "0=物种树, 1=基因树, 2=GC含量, 3=占据率, 4=分支统计, 5=相对频率"
            ),
        )
        parser.add_argument(
            "-p", "--path", dest="path", default=None,
            help="数据目录路径 / Path to the gene directory or species tree",
        )
        parser.add_argument(
            "-r", "--rooting", dest="root", default=None,
            help="根定义文件路径 / The rooting file",
        )
        parser.add_argument(
            "-s", "--style", dest="style", type=int, default=0,
            help="颜色样式集 / The color style set",
        )
        parser.add_argument(
            "-t", "--threshold", dest="thresh", default=None,
            help="自展支持阈值 / The bootstrap threshold",
        )
        parser.add_argument(
            "-x", "--modelCond", dest="modelCond", default=None,
            help="占据率分析中指定的单一模型条件",
        )
        parser.add_argument(
            "-y", dest="newModel", default=None,
            help="模型条件重排文件 / New order for model conditions",
        )
        parser.add_argument(
            "-w", dest="newOrder", default=None,
            help="进化支重排文件 / New order for clades",
        )
        parser.add_argument(
            "-k", "--missing", dest="missing", default=0,
            help="缺失数据标志 (1=部分缺失视为完整) / Missing data handling flag",
        )
        parser.add_argument(
            "-o", "--output", dest="label", default=None,
            help="输出目录 / Name of the output folder",
        )
        parser.add_argument(
            "-g", "--outgroup", dest="outg", default=None,
            help="相对频率分析中的外群名称 / Name of the outgroup",
        )
        return parser

    @classmethod
    def _from_namespace(cls, parser: argparse.ArgumentParser,
                        ns: argparse.Namespace) -> "Options":
        # 验证 path
        if not ns.path:
            parser.print_help()
            sys.exit("请输入数据目录路径 / Please enter the path to the data folder.")
        path = os.path.abspath(os.path.expanduser(ns.path))
        if not os.path.exists(path):
            parser.print_help()
            sys.exit("数据目录不存在 / Data directory does not exist.")

        # 验证 mode
        if ns.mode is None:
            parser.print_help()
            sys.exit(
                "请输入分析模式 / Please enter the mode. "
                "0=species tree, 1=gene tree, 2=GC, 3=occupancy, 4=branch, 5=freq."
            )
        mode = int(ns.mode)
        if mode not in (0, 1, 2, 3, 4, 5):
            parser.print_help()
            sys.exit("无效的分析模式 / Invalid mode. Use 0-5.")

        # 验证 label (output)
        label = ns.label
        if not label:
            parser.print_help()
            sys.exit("请输入输出目录 / Please enter the output folder.")
        label = os.path.abspath(label)
        os.makedirs(label, exist_ok=True)

        # threshold
        threshold = -1.0
        if mode in (0, 1):
            if ns.thresh is None:
                parser.print_help()
                sys.exit("请输入自展阈值 / Please enter the bootstrap threshold.")
            threshold = float(ns.thresh)

        # clades
        clades = ""
        if mode in (0, 1):
            if not ns.clades:
                parser.print_help()
                sys.exit("请输入进化支定义文件 / Please enter the clade definition file.")
            clades = os.path.abspath(ns.clades)
            if not os.path.isfile(clades):
                parser.print_help()
                sys.exit("进化支定义文件不存在 / Clade definition file not found.")

        # root
        root = ""
        if mode == 4:
            if not ns.root:
                parser.print_help()
                sys.exit("请输入根定义文件 / Please enter the rooting definition file.")
            root = os.path.abspath(ns.root)
            if not os.path.isfile(root):
                parser.print_help()
                sys.exit("根定义文件不存在 / Rooting definition file not found.")

        # annotation
        annotation = ""
        if mode in (3, 5):
            if not ns.annotation:
                parser.print_help()
                sys.exit("请输入注释文件 / Please enter the annotation file.")
            annotation = os.path.abspath(ns.annotation)
            if not os.path.isfile(annotation):
                parser.print_help()
                sys.exit("注释文件不存在 / Annotation file not found.")

        # outgroup
        outg = ""
        if mode == 5 and ns.outg:
            outg = ns.outg

        # missing
        missing = int(ns.missing) if ns.missing is not None else 0

        # names file (auto-generated from annotation)
        names = ""
        if annotation:
            names = os.path.join(os.path.dirname(annotation), "names.txt")
            cls._create_names_file(annotation, names)

        # file search patterns
        search, search_thr, search_rooted, search_thr_rooted = \
            cls._build_search_patterns(mode, path, threshold)

        return cls(
            path=path,
            mode=mode,
            annotation=annotation,
            clades=clades,
            root=root,
            threshold=threshold,
            label=label,
            model_cond=ns.modelCond,
            new_model=ns.newModel,
            new_order=ns.newOrder,
            missing=missing,
            style=ns.style,
            outg=outg,
            names=names,
            search=search,
            search_thr=search_thr,
            search_rooted=search_rooted,
            search_thr_rooted=search_thr_rooted,
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _build_search_patterns(mode: int, path: str,
                               thresh: float) -> Tuple:
        """根据分析模式构建文件搜索 glob 模式。"""
        # Format threshold to match the file suffix generated by
        # TreeTools.remove_edges_from_tree (int if > 1, else float as-is)
        if thresh > 1:
            thresh_str = str(int(thresh))
        else:
            thresh_str = str(thresh)

        if mode == 0:
            s = f"{path}/*/estimated_species_tree.tree"
            st = f"{path}/*/estimated_species_tree.tree.{thresh_str}"
            sr = f"{path}/*/estimated_species_tree.tree"
            str_ = f"{path}/*/estimated_species_tree.tree.{thresh_str}"
        elif mode == 1:
            s = f"{path}/*/*/estimated_gene_trees.tree"
            st = f"{path}/*/*/estimated_gene_trees.tree.{thresh_str}"
            sr = f"{path}/*/*/estimated_gene_trees.tree"
            str_ = f"{path}/*/*/estimated_gene_trees.tree.{thresh_str}"
        elif mode == 2:
            s = f"{path}/*/*-alignment-noFilter.fasta"
            st = sr = str_ = None
        elif mode == 3:
            s = f"{path}/*/*-alignment-*.fasta"
            st = sr = str_ = None
        elif mode == 4:
            s = f"{path}/*/*-estimated_gene_trees.tree"
            sr = f"{path}/*/*-estimated_gene_trees.tree.rerooted"
            st = str_ = None
        elif mode == 5:
            s = st = sr = str_ = None
        else:
            s = st = sr = str_ = None
        return s, st, sr, str_

    @staticmethod
    def _create_names_file(annotation: str, names_path: str) -> None:
        """从注释文件提取物种名称，写入 names.txt。"""
        with open(annotation, "r") as g, open(names_path, "w") as f:
            for line in g:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t")
                taxon = parts[0].replace("_", " ")
                f.write(taxon + "\n")

    @property
    def multiplier(self) -> float:
        """阈值乘数：若阈值 <= 1.0 则乘以 100（本地后验概率→百分比）。"""
        return 100.0 if self.threshold <= 1.0 else 1.0
