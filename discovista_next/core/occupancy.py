"""
占据率分析模块
==============

替代原 ``occupancy.R`` 的数据预处理部分。计算各物种在不同基因中的序列占据率，
并按进化支聚合统计。可视化由 ``discovista_next.viz`` 模块完成。
"""

import os
import re
import sys
from collections import defaultdict
from typing import Dict, List, Set, Tuple

import pandas as pd

from .tree_tools import TreeTools


class Occupancy:
    """占据率分析器。

    从 FASTA 比对文件计算每个物种在每条基因/模型条件中的序列长度，
    然后生成统计数据用于可视化。
    """

    # ------------------------------------------------------------------
    @classmethod
    def compute_occupancy(cls, search_pattern: str, out_file: str) -> pd.DataFrame:
        """计算占据率数据并保存为 CSV。

        Parameters
        ----------
        search_pattern : str
            FASTA 比对文件的 glob 模式。
        out_file : str
            输出 CSV 文件路径。

        Returns
        -------
        pd.DataFrame
            包含占据率数据的 DataFrame。
        """
        TreeTools.occupancy(search_pattern, out_file)
        print(f"All occupancy stats written to {out_file}")

        # 读取 CSV
        df = pd.read_csv(out_file, sep=" ", header=None,
                          names=["Seq", "GENE_ID", "model_condition",
                                 "Taxon", "Len"])
        df["V5"] = pd.to_numeric(df["Len"], errors="coerce")
        df = df[df["Len"] != 0].copy()

        # 创建 ID = Seq-model_condition
        df["ID"] = df["Seq"].astype(str) + "-" + df["model_condition"].astype(str)
        return df

    # ------------------------------------------------------------------
    @classmethod
    def analyze(cls, search_pattern: str, annotation_file: str,
                out_dir: str, model_cond: str = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """执行完整占据率分析。

        Parameters
        ----------
        search_pattern : str
            FASTA 比对文件的 glob 模式。
        annotation_file : str
            注释文件路径 (tab 分隔: 物种名\\t进化支名)。
        out_dir : str
            输出目录。
        model_cond : str, optional
            仅分析指定的模型条件。

        Returns
        -------
        (df_species, df_clades)
            物种级占据率 DataFrame 和进化支级占据率 DataFrame。
        """
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "occupancy.csv")

        df = cls.compute_occupancy(search_pattern, out_file)

        max_g = df["GENE_ID"].nunique()

        # 物种级统计
        tc = df.groupby(["ID", "Taxon"]).size().reset_index(name="occupancy")
        tc["occupancy_prob"] = tc["occupancy"] / max_g
        tc["miss_prob"] = 1 - tc["occupancy_prob"]

        # 按进化支合并
        clades = pd.read_csv(annotation_file, sep="\t", header=None,
                              names=["Names", "Clade"])
        df_merged = df.merge(clades, left_on="Taxon", right_on="Names")

        # 每个进化支在每条基因中出现的次数
        tc_clades = (df_merged.groupby(["GENE_ID", "ID", "Clade"])
                      .size()
                      .reset_index(name="num_clade_present"))

        # 进化支占据率 = 该进化支出现的基因数 / 总基因数
        tc_clades_agg = (tc_clades.groupby(["ID", "Clade"])
                         .apply(lambda x: (x["num_clade_present"] > 0).sum()
                                / df["GENE_ID"].nunique())
                         .reset_index(name="clade_occupancy"))

        # 保存
        tc.to_csv(os.path.join(out_dir, "occupancy-final.csv"),
                   index=False, sep="\t")
        tc_clades_agg.to_csv(os.path.join(out_dir, "occupancy-clades-final.csv"),
                              index=False, sep="\t")

        # 单一模型条件的 tile map
        if model_cond:
            df_single = df[df["ID"] == model_cond].copy()
            if not df_single.empty:
                df_single = df_single.groupby(["GENE_ID", "Taxon"])["Len"] \
                    .sum().reset_index()

        return tc, tc_clades_agg
