"""
进化支单系性分析模块
====================

替代原 ``find_clades2.py``，用于检测系统发育树中预定义进化支的单系性。

分类状态:
  - IS_MONO:              完全单系
  - IS_MONO_INCOMPLETE:   单系但不完整（部分物种缺失）
  - CAN_MONO:             可兼容（低支持分支收缩后变为单系）
  - CAN_MONO_INCOMPLETE:  可兼容但不完整
  - NOT_MONO:             非单系
  - NO_CLADE:             进化支物种不足
  - COMP_MISSING:         关键组成部分完全缺失
"""

import os
import re
import sys
from typing import Dict, List, Optional, Set, Tuple

import dendropy


def get_present_taxa(tree: dendropy.Tree, labels) -> list:
    """在树中查找存在的类群。"""
    result = []
    for label in labels:
        node = tree.find_node_with_taxon_label(label)
        if node is not None:
            result.append(node.taxon)
    return result


def represents_number(s) -> bool:
    try:
        float(s)
        return True
    except (TypeError, ValueError):
        return False


class CladeAnalyzer:
    """进化支单系性检测器。

    读取进化支定义文件，对每棵树检测各进化支的状态。
    """

    def __init__(self, taxa: Set[str], out_file: str):
        self.allclades: Dict[str, list] = {}
        self.clades: Dict[str, list] = {}
        self.clade_comps: Dict[str, list] = {}
        self.othercomps: Dict[str, list] = {}
        self.alltaxa: Set[str] = taxa
        self.letters: Dict[str, str] = {}
        self.outFile: str = out_file
        self.show: Dict[str, int] = {}

    # ------------------------------------------------------------------
    def read_clades(self, filename: str) -> None:
        """读取进化支定义文件。

        文件格式 (tab 分隔):
          Clade Name | Clade Definition | Section Letter | Components |
          Show | Comments
        """
        for line in open(filename):
            line = line.rstrip("\n")
            r = line.split("\t")
            if len(r) > 1:
                r[0] = r[0].strip()
                r[1] = r[1].strip()
            else:
                print(f"Line '{line}' is not tab-separated!")
                sys.exit(1)
            if r[0] == "Clade Name":
                continue

            sign = "+"
            clade = set()
            for x in re.split(r"([+|-])", r[1]):
                try:
                    if x in ("+", "-"):
                        sign = x
                    else:
                        x = x.strip('"')
                        if x in self.alltaxa:
                            new = {x}
                        elif x in self.allclades:
                            new = set(self.allclades[x])
                        else:
                            raise KeyError(x)
                        if sign == "+":
                            clade.update(new)
                        else:
                            clade.difference_update(new)
                except KeyError as e:
                    print(f"In {r[0]}, {e.args[0]} is not defined before")
                    sys.exit(1)

            clade = list(clade)

            # Components (column 4)
            if len(r) >= 4 and r[3].strip():
                components = r[3].strip().split("+")
            else:
                components = []

            # Show (column 5)
            if len(r) >= 5:
                show_str = r[4].strip()
                if show_str == "":
                    print(f"Column 5 takes 0/1, but got nothing! Line: {line}")
                    sys.exit(1)
                if represents_number(show_str):
                    show = int(show_str)
                    if show not in (0, 1):
                        print(f"Column 5 takes 0/1! Got {show_str}. Line: {line}")
                        sys.exit(1)
                else:
                    print(f"Column 5 takes 0/1, got string! Line: {line}")
                    sys.exit(1)
            else:
                show = 1

            # Other components (column 6)
            if len(r) >= 6 and r[5].strip():
                othercomponents = r[5].strip().split("+")
            else:
                othercomponents = []

            name = r[0]
            self.letters[name] = r[2] if len(r) >= 4 else ""
            self.allclades[name] = clade
            if len(r) >= 4 and r[3] != "None":
                self.clades[name] = clade
                self.clade_comps[name] = components
            self.othercomps[name] = othercomponents
            self.show[name] = show

    # ------------------------------------------------------------------
    def _get_support_from_bipartition(self, tree, clade, mult):
        """从树的双分中获取支持值和分支长度。"""
        bipartition = tree.taxon_namespace.taxa_bipartition(
            taxa=clade, is_mutable=False)
        clade2 = {c.taxon for c in tree.leaf_nodes()} - set(clade)
        bipartition2 = tree.taxon_namespace.taxa_bipartition(
            taxa=clade2, is_mutable=False)

        bipartition.is_mutable = False
        bipartition2.is_mutable = False

        e = tree.bipartition_edge_map.get(bipartition)
        e2 = tree.bipartition_edge_map.get(bipartition2)

        if bipartition.is_trivial() or bipartition2.is_trivial():
            if float(mult) < 100:
                return (1.0, e.length if e else None)
            else:
                return (100.0, e.length if e else None)

        if e is not None and e.label is None:
            return (e2.label if e2 else None,
                    e2.length if e2 else None)
        else:
            return (e.label if e else None, e.length if e else None)

    # ------------------------------------------------------------------
    def _print_result(self, tree_name, keyword, bipartition, lst,
                      tree, ofile, mult, clade):
        ln = "_".join(str(l) for l in lst) if isinstance(lst, list) else lst
        letter = self.letters.get(ln, "")
        name = f"{ln} ({letter})" if letter else ln

        if keyword in ("IS_MONO", "IS_MONO_INCOMPLETE"):
            support, length = self._get_support_from_bipartition(tree, clade, mult)
            if support is None:
                print(f"WARNING: support not available. clade={clade}")
            if represents_number(support) and represents_number(mult):
                support = str(float(support) * float(mult))
            else:
                support = "None"
                length = "None"
        else:
            support = "None"
            length = "None"

        try:
            ofile.write(f"{tree_name}\t{keyword}\t{support}\t{name}\t{length}\n")
        except IOError:
            print(f"Cannot write results for tree {tree_name} and clade {name}")
            sys.exit(1)

    # ------------------------------------------------------------------
    def _is_mono(self, tree, clade, all_biparts):
        taxon_namespace = tree.taxon_namespace
        bipartition = taxon_namespace.taxa_bipartition(taxa=clade)
        bipartition = bipartition.compile_split_bitmask()
        all_biparts = set(all_biparts)
        return (bipartition in all_biparts), bipartition

    def _can_mono(self, tree, clade):
        bipartition = tree.taxon_namespace.taxa_bipartition(taxa=clade)
        can_mono = tree.is_compatible_with_bipartition(
            bipartition, is_bipartitions_updated=False)
        return can_mono, bipartition

    def _check_mono(self, tree, tree_name, clade, name, complete,
                     ofile, mult, all_biparts):
        m, bipartition = self._is_mono(tree, clade, all_biparts)
        if m:
            if complete:
                self._print_result(tree_name, "IS_MONO", bipartition,
                                    name, tree, ofile, mult, clade)
            else:
                self._print_result(tree_name, "IS_MONO_INCOMPLETE", bipartition,
                                    name, tree, ofile, mult, clade)
            return
        c, bipartition = self._can_mono(tree, clade)
        if c and not m:
            if complete:
                self._print_result(tree_name, "CAN_MONO", bipartition,
                                    name, tree, ofile, mult, clade)
            else:
                self._print_result(tree_name, "CAN_MONO_INCOMPLETE", bipartition,
                                    name, tree, ofile, mult, clade)
            return
        self._print_result(tree_name, "NOT_MONO", bipartition,
                            name, tree, ofile, mult, clade)

    # ------------------------------------------------------------------
    def _analyze_clade(self, name, clade, comps, tree, tree_name,
                       mult, all_biparts):
        ofile = open(self.outFile, "a+")
        taxa = get_present_taxa(tree, clade)
        other_taxa_labels = self.alltaxa - set(clade)
        taxa_labels = {t.label for t in taxa}
        other_side_taxa = get_present_taxa(tree, other_taxa_labels)
        othercomps = self.othercomps.get(name, [])
        other_taxa_labels = {t.label for t in other_side_taxa}

        if comps:
            for comp in comps:
                if comp in self.allclades:
                    if not (set(self.allclades[comp]) & taxa_labels):
                        self._print_result(tree_name, "COMP_MISSING", None,
                                            name, tree, ofile, mult, clade)
                        ofile.close()
                        return
                else:
                    print(f"Component '{comp}' not defined for clade '{name}'")
                    sys.exit(1)

        if othercomps:
            for comp in othercomps:
                if comp:
                    if comp in self.allclades:
                        if not (set(self.allclades[comp]) & other_taxa_labels):
                            self._print_result(tree_name, "COMP_MISSING", None,
                                                name, tree, ofile, mult, clade)
                            ofile.close()
                            return
                    else:
                        print(f"Other component '{comp}' not defined for clade '{name}'")
                        sys.exit(1)

        if len(taxa) < 2 or len(other_side_taxa) < 2:
            self._print_result(tree_name, "NO_CLADE", None,
                                name, tree, ofile, mult, clade)
        else:
            self._check_mono(tree, tree_name, taxa, name,
                              len(taxa) == len(clade),
                              ofile, mult, all_biparts)
        ofile.close()

    # ------------------------------------------------------------------
    def analyze(self, tree: dendropy.Tree, tree_name: str, mult: float):
        """对单棵树执行所有进化支分析。"""
        for nd in tree.postorder_node_iter():
            nd.edge.label = nd.label
        tree_tmp = tree.clone(depth=1)
        all_biparts = [
            t.compile_split_bitmask()
            for t in tree_tmp.encode_bipartitions(is_bipartitions_mutable=True)
        ]
        self.alltaxa = set(self.allclades.get("All", self.alltaxa))

        for k, v in self.allclades.items():
            if self.show.get(k, 0) == 1:
                clade_comp = self.clade_comps.get(k)
                self._analyze_clade(k, v, clade_comp, tree, tree_name,
                                     mult, all_biparts)

    # ------------------------------------------------------------------
    @staticmethod
    def get_taxa_from_clade_file(clade_file: str) -> Set[str]:
        """从进化支定义文件中提取名为 'All' 的进化支包含的所有物种。"""
        taxa = set()
        with open(clade_file, "r") as f:
            for line in f:
                fields = line.split("\t")
                if fields[0] == "All":
                    list_line = fields[1] if len(fields) > 1 else ""
                    raw = list_line.replace('""+""', "\t") \
                                   .replace('""', "\t") \
                                   .replace('"', "\t") \
                                   .replace("+", "\t") \
                                   .strip("\t") \
                                   .replace("\t\t", "\t")
                    taxa = set(raw.split("\t"))
                    taxa.discard("")
        if not taxa:
            print("Please define a clade named 'All' with all species!")
            sys.exit(1)
        return taxa

    # ------------------------------------------------------------------
    @classmethod
    def run(cls, names_file: str, clades_file: str, out_file: str,
            mult: float, tree_files_str: str) -> None:
        """主入口：分析多棵树中的进化支单系性。

        Parameters
        ----------
        names_file : str
            物种名称文件路径。
        clades_file : str
            进化支定义文件路径。
        out_file : str
            结果输出文件路径。
        mult : float
            支持值乘数。
        tree_files_str : str
            以空格分隔的树文件路径字符串。
        """
        taxa = cls.get_taxa_from_clade_file(clades_file)
        if not taxa:
            print("Your clade 'All' has some problem!")
            sys.exit(1)

        analyzer = cls(taxa, out_file)
        analyzer.read_clades(clades_file)

        file_names = tree_files_str.split(" ")
        if not file_names:
            print("No tree files found!")
            sys.exit(1)
        print(f"Number of trees to analyze: {len(file_names)}")

        for file_name in file_names:
            if not os.path.exists(file_name):
                print("Tree file does not exist!")
                sys.exit(1)
            try:
                trees = dendropy.TreeList.get(
                    path=file_name, schema="newick",
                    rooting="force-unrooted",
                    preserve_underscores=True)
            except ValueError:
                print("Cannot read tree file!")
                raise

            labels_set = {t.label for t in trees.taxon_namespace}
            name_mismatch = labels_set - taxa
            if name_mismatch:
                print(f"The following taxa are not found in names file:\n"
                      f" {name_mismatch}", file=sys.stderr)
                continue

            for i, tree in enumerate(trees):
                tree_name = f"{file_name}_{i}"
                try:
                    analyzer.analyze(tree, tree_name, mult)
                except ValueError:
                    print(f"Analyzing tree {tree_name} failed!")
                    raise
