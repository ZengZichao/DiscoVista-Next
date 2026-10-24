"""
分析控制器模块
==============

替代原 ``analyze.py`` 中的 ``Analyze`` 类。协调核心分析模块和可视化模块，
完成完整的分析流程。所有对 R 脚本的调用都已移除，改为直接调用 Python 可视化模块。
"""

import glob
import os
import re
import sys
from typing import Optional

from .config import Options
from .tree_tools import TreeTools
from .find_clades import CladeAnalyzer
from .gc_stats import GCStats
from .occupancy import Occupancy
from .relative_freq import RelativeFrequency

from ..viz.depict_clades import DepictClades
from ..viz.gc_plot import GCPlot
from ..viz.occupancy_plot import OccupancyPlot
from ..viz.branch_stat_plot import BranchStatPlot
from ..viz.tree_plot import TreePlot
from ..viz.relative_freq_plot import RelativeFreqPlot

import pandas as pd


class Analyzer:
    """分析控制器，根据分析模式协调各模块。"""

    def __init__(self, opt: Options):
        self.opt = opt

    # ------------------------------------------------------------------
    def analyze(self) -> None:
        """根据模式执行对应的分析。"""
        mode = self.opt.mode
        if mode == 0 or mode == 1:
            self.trees_analysis()
        elif mode == 2:
            self.gc_stat_analysis()
        elif mode == 3:
            self.occupancy_analysis()
        elif mode == 4:
            self.gene_tree_branch_info()
        elif mode == 5:
            self.rel_freq()

    # ------------------------------------------------------------------
    def trees_analysis(self) -> None:
        """物种树/基因树不一致性分析 (mode 0, 1)。"""
        opt = self.opt
        out_file = os.path.join(opt.label, "clades.txt")
        out_file_thr = os.path.join(opt.label, "clades.hs.txt")
        finegrained = os.path.join(opt.label, "finegrained")
        os.makedirs(finegrained, exist_ok=True)

        # 收集树文件
        search_files = sorted(glob.glob(opt.search))
        if not search_files:
            print("No tree found! Please follow the structure specified in examples!")
            sys.exit(1)
        print(f"Number of trees found: {len(search_files)}")

        # 收缩低支持分支
        for tree in search_files:
            try:
                TreeTools.remove_edges_from_tree(tree, opt.threshold)
            except ValueError:
                print("Error in contracting low support branches")
                raise

        # 收集收缩后的树文件
        search_thr_files = sorted(glob.glob(opt.search_thr))
        if not search_thr_files:
            print("No contracted tree found!")
            sys.exit(1)
        print(f"Number of contracted trees: {len(search_thr_files)}")

        search_rooted = sorted(glob.glob(opt.search_rooted))
        search_thr_rooted = sorted(glob.glob(opt.search_thr_rooted))

        # 进化支分析
        try:
            CladeAnalyzer.run(opt.names, opt.clades, out_file,
                              opt.multiplier, " ".join(search_rooted))
        except ValueError:
            print("An error occurred during tree analysis!")
            raise

        try:
            CladeAnalyzer.run(opt.names, opt.clades, out_file_thr,
                              opt.multiplier, " ".join(search_thr_rooted))
        except ValueError:
            print("An error occurred during tree analysis!")
            raise

        # 后处理结果文件
        out_res = out_file + ".res"
        out_res_thr = out_file_thr + ".res"

        self._postprocess_results(out_file, out_res)
        self._postprocess_results(out_file_thr, out_res_thr)

        # 可视化
        self._depict_clades(out_res, out_res_thr, opt.mode)

    # ------------------------------------------------------------------
    def _postprocess_results(self, in_file: str, out_res: str) -> None:
        """将结果文件转换为标准格式。"""
        with open(in_file, "r") as f:
            with open(out_res, "w") as o:
                o.write("ID\tDS\tMONO\tBOOT\tCLADE\tBRANCHLEN\n")
                for line in f:
                    linet = line.strip()
                    parts = linet.split("\t")
                    b = os.path.basename(os.path.dirname(parts[0]))
                    ID = b
                    tmp = re.split("-", b)
                    method = tmp[-1]
                    mono = parts[1]
                    boot = parts[2]
                    clade = re.sub(r"\s+\(.*", "", parts[3])
                    branchlen = parts[4] if len(parts) > 4 else ""
                    o.write(f"{ID}\t{method}\t{mono}\t{boot}\t{clade}\t{branchlen}\n")

    # ------------------------------------------------------------------
    def _depict_clades(self, file_res: str, file_res_thr: str,
                       mode: int) -> None:
        """调用可视化模块绘制进化支图。"""
        opt = self.opt
        is_species = (mode == 0)
        depict = DepictClades(opt.label, is_species_tree=is_species,
                              missing_flag=opt.missing)

        # 读取重排文件
        new_clades = None
        new_models = None
        if opt.new_order:
            new_clades = pd.read_csv(opt.new_order, sep="\t", header=None)
        if opt.new_model:
            new_models = pd.read_csv(opt.new_model, sep="\t", header=None)

        # 读取进化支定义文件以获取排序
        clade_order = None
        if opt.clades:
            try:
                cl_df = pd.read_csv(opt.clades, sep="\t")
                if "Section Letter" in cl_df.columns:
                    grouped = cl_df[cl_df["Section Letter"] != "None"]
                    clade_order = []
                    for section in grouped["Section Letter"].dropna().unique():
                        clade_order.append(f"[{section}]")
                        for _, row in grouped[grouped["Section Letter"] == section].iterrows():
                            clade_order.append(str(row["Clade Name"]))
            except Exception:
                pass

        data = depict.read_data(file_res, file_res_thr,
                                 clade_order=clade_order,
                                 new_clades=new_clades,
                                 new_models=new_models)

        if is_species:
            depict.plot_block(data)
            depict.plot_block_shades(data)
        else:
            depict.plot_bargraphs(data)
            depict.plot_bargraphs_proportion(data)
            depict.plot_histograms(data)

    # ------------------------------------------------------------------
    def gc_stat_analysis(self) -> None:
        """GC 含量分析 (mode 2)。"""
        opt = self.opt
        out_file = os.path.join(opt.label, "gc-stat.csv")
        GCStats.run_analysis(opt.search, out_file)

        # 可视化
        gc_plot = GCPlot(opt.label)
        gc_plot.run(out_file)

    # ------------------------------------------------------------------
    def occupancy_analysis(self) -> None:
        """占据率分析 (mode 3)。"""
        opt = self.opt
        out_file = os.path.join(opt.label, "occupancy.csv")
        df = Occupancy.compute_occupancy(opt.search, out_file)

        max_g = df["GENE_ID"].nunique()

        # 物种级统计
        tc = df.groupby(["ID", "Taxon"]).size().reset_index(name="occupancy")

        # 进化支统计
        clades = pd.read_csv(opt.annotation, sep="\t", header=None,
                              names=["Names", "Clade"])
        df_merged = df.merge(clades, left_on="Taxon", right_on="Names")
        tc_clades = (df_merged.groupby(["GENE_ID", "ID", "Clade"])
                      .size().reset_index(name="num_clade_present"))
        tc_clades_agg = (tc_clades.groupby(["ID", "Clade"])
                          .apply(lambda x: (x["num_clade_present"] > 0).sum()
                                 / df["GENE_ID"].nunique())
                          .reset_index(name="clade_occupancy"))

        # 保存
        tc.to_csv(os.path.join(opt.label, "occupancy-final.csv"),
                   index=False, sep="\t")
        tc_clades_agg.to_csv(
            os.path.join(opt.label, "occupancy-clades-final.csv"),
            index=False, sep="\t")

        # 可视化
        occ_plot = OccupancyPlot(opt.label)
        single_model_df = None
        if opt.model_cond:
            single_model_df = df[df["ID"] == opt.model_cond].copy()
        occ_plot.run(tc, tc_clades_agg, max_g, single_model_df)

    # ------------------------------------------------------------------
    def gene_tree_branch_info(self) -> None:
        """分支统计 vs 分支长度分析 (mode 4)。"""
        opt = self.opt
        search_files = sorted(glob.glob(opt.search))
        for tree in search_files:
            TreeTools.reroot(tree, opt.root, opt.annotation, 1)

        tree_names = sorted(glob.glob(opt.search_rooted))
        out_file = os.path.join(opt.label, "branchStats.csv")
        out_file2 = os.path.join(opt.label, "branchSupport.csv")
        TreeTools.branch_info(tree_names, out_file, out_file2)
        print(f"Branch length and support values written to {out_file}")

        # 可视化
        bs_plot = BranchStatPlot(opt.label)
        bs_plot.run(out_file, out_file2)

    # ------------------------------------------------------------------
    def rel_freq(self) -> None:
        """相对频率分析 (mode 5)。"""
        opt = self.opt
        out_dir = RelativeFrequency.run(
            opt.path, opt.annotation, opt.names,
            opt.label, opt.outg)

        # 可视化
        freq_file = os.path.join(out_dir, "freqQuadCorrected.csv")
        if os.path.exists(freq_file):
            rf_plot = RelativeFreqPlot(opt.label)
            rf_plot.run(freq_file)

            # 绘制树图
            tree_file = os.path.join(out_dir, "estimated_species_tree.tree")
            if os.path.exists(tree_file):
                tree_plot = TreePlot(opt.label)
                tree_plot.plot_tree(tree_file)
        else:
            print("freqQuadCorrected.csv not found. Skipping visualization.")
