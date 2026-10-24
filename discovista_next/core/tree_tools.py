"""
树操作工具模块
=============

替代原 ``tools.py``，使用 ``dendropy`` 进行 Newick 树的读取、写入、
重根、低支持分支收缩、分支信息统计等操作。

全部代码兼容 Python 3。
"""

import glob
import os
import re
import sys
import statistics
from typing import List, Optional, Set, Tuple

import dendropy


class TreeTools:
    """封装所有与 Newick 系统发育树相关的底层操作。"""

    # ------------------------------------------------------------------
    # 基本工具函数
    # ------------------------------------------------------------------
    @staticmethod
    def is_number(s) -> bool:
        try:
            float(s)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def mean(data: List[float]) -> float:
        if len(data) < 1:
            raise ValueError("mean requires at least one data point")
        return sum(data) / len(data)

    @staticmethod
    def median(data: List[float]) -> float:
        if len(data) < 1:
            raise ValueError("median requires at least one data point")
        return statistics.median(data)

    @staticmethod
    def pstdev(data: List[float]):
        n = len(data)
        if n < 1:
            raise ValueError("variance requires at least two data points")
        if n == 1:
            return "NA"
        return statistics.pstdev(data)

    @staticmethod
    def simplify_fasta(filename: str) -> str:
        """将多行 FASTA 压缩为单行序列格式，返回纯文本。"""
        tmpfile = filename + ".tmp"
        with open(filename, "r") as f, open(tmpfile, "w") as g:
            for line in f:
                line = line.rstrip("\n")
                r = re.sub(r">(.*)", r"@>\1@", line)
                g.write(r)
        with open(tmpfile, "r") as g:
            content = g.read()
        content = re.sub("@", "\n", content)
        content = re.sub(r"^\n", "", content)
        os.remove(tmpfile)
        return content

    @staticmethod
    def read_roots(root_file: str) -> List[List[str]]:
        """读取根定义文件，每行为一个外群物种集合。"""
        roots = []
        with open(root_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                roots.append(line.split(" "))
        return roots

    # ------------------------------------------------------------------
    # 树操作
    # ------------------------------------------------------------------
    @staticmethod
    def remove_edges_from_tree(tree_file: str, threshold,
                               output_file: Optional[str] = None,
                               strip_internal: bool = False,
                               strip_bl: bool = False) -> None:
        """收缩树中支持值低于阈值的分支（即合并相应内部节点）。

        Parameters
        ----------
        tree_file : str
            Newick 格式树文件路径。
        threshold : float or int
            支持值阈值，低于此值的分支将被收缩。
        output_file : str, optional
            输出文件路径。默认为 ``tree_file.threshold``。
        strip_internal : bool
            是否移除内部节点标签。
        strip_bl : bool
            是否移除分支长度。
        """
        if not os.path.exists(tree_file):
            print(f"treeName: {tree_file} is not found!")
            sys.exit(1)

        t = float(threshold)
        if t > 1:
            t = int(t)

        results_file = output_file if output_file else f"{tree_file}.{t}"

        trees = dendropy.TreeList.get(path=tree_file, schema="newick")

        def _should_remove(edge):
            # Only collapse internal edges (edges leading to internal nodes)
            # Terminal edges (leaf edges) cannot be collapsed
            if edge.head_node is not None and edge.head_node.is_leaf():
                return False
            if edge.label is None:
                return True
            if TreeTools.is_number(edge.label) and float(edge.label) >= t:
                return False
            return True

        for tree in trees:
            for n in tree.internal_nodes():
                if n.label is not None:
                    try:
                        n.label = float(n.label)
                        n.edge.label = n.label
                    except (ValueError, TypeError):
                        pass
            edges = set(tree.edges(filter_fn=_should_remove))
            print(f"{len(edges)} edges will be removed", file=sys.stderr)
            for e in edges:
                try:
                    e.collapse()
                except ValueError:
                    # Skip edges that cannot be collapsed (e.g. terminal edges)
                    pass
            if strip_internal:
                for n in tree.internal_nodes():
                    n.label = None
            if strip_bl:
                for e in tree.get_edge_set():
                    e.length = None

        trees.write(file=open(results_file, "w"), schema="newick",
                    suppress_rooting=True)

    @staticmethod
    def root(rootgroup: Set[str], tree: dendropy.Tree):
        """在给定外群集合的中点处重根树。

        返回新的根节点，若外群不存在则返回 None。
        """
        root_node = None
        biggest = 0
        old_root = tree.seed_node
        for n in tree.postorder_node_iter():
            if n.is_leaf():
                n.r = n.taxon.label in rootgroup if n.taxon else False
                n.s = 1
            else:
                n.r = all(getattr(a, "r", False) for a in n.child_nodes())
                n.s = sum(getattr(a, "s", 0) for a in n.child_nodes())
            if n.r and biggest < n.s:
                biggest = n.s
                root_node = n
        if root_node is None:
            return None

        newlen = root_node.edge.length / 2 if root_node.edge.length else None
        tree.reroot_at_edge(root_node.edge, length1=newlen, length2=newlen,
                            suppress_unifurcations=False)
        # 修正内部节点标签（当作为支持值处理时）
        while (old_root.parent_node != tree.seed_node
               and old_root.parent_node is not None):
            old_root.label = old_root.parent_node.label
            old_root = old_root.parent_node
            if len(old_root.sister_nodes()) > 0:
                old_root.label = old_root.sister_nodes()[0].label
        tree.suppress_unifurcations()
        return root_node

    @staticmethod
    def reroot(tree_file: str, root_def: str, annotation: str,
               if_print: int = 1, results_file: Optional[str] = None) -> None:
        """对树文件按根定义进行重根操作。"""
        if results_file is None:
            results_file = f"{tree_file}.rerooted"

        trees = dendropy.TreeList.get(path=tree_file, schema="newick",
                                       rooting="force-rooted",
                                       preserve_underscores=True)
        ROOTS = TreeTools.read_roots(root_def)
        lst = []
        for i, tree in enumerate(trees):
            roots = list(ROOTS)
            while roots and TreeTools.root(set(roots[0]), tree) is None:
                roots = roots[1:]
            if not roots:
                lst.append(i)
                print(f"Tree {i}: none of the root groups exist. "
                      f"Leaving unrooted.")
        if if_print == 0:
            for i in sorted(lst, reverse=True):
                del trees[i]
        print(f"writing results to {results_file}")
        trees.write(path=results_file, schema="newick",
                    suppress_rooting=True,
                    suppress_leaf_node_labels=False,
                    unquoted_underscores=True)

    # ------------------------------------------------------------------
    # 分支信息
    # ------------------------------------------------------------------
    @staticmethod
    def leaf_to_leaf_distances(tree: dendropy.Tree) -> List[float]:
        """计算所有叶节点之间的路径距离。"""
        pdm = tree.phylogenetic_distance_matrix()
        list_taxon = {n.taxon for n in tree.leaf_node_iter()}
        br_len = []
        for taxon1 in tree.taxon_namespace:
            if taxon1 not in list_taxon:
                continue
            for taxon2 in tree.taxon_namespace:
                if taxon2 not in list_taxon:
                    continue
                dist = pdm.patristic_distance(taxon1, taxon2)
                br_len.append(dist)
        return br_len

    @staticmethod
    def branch_supports(tree: dendropy.Tree, ds: str, model: str,
                        out_file) -> List[float]:
        """收集非平凡分支的支持值并写入文件。"""
        tree.encode_bipartitions()
        supp = []
        for n in tree.postorder_node_iter():
            if n.is_leaf():
                continue
            if n.edge.bipartition.is_trivial():
                continue
            if n.label is not None:
                supp.append(float(n.label))
                out_file.write(f"{ds} {model} {n.label}\n")
        return supp

    @staticmethod
    def branch_info(tree_files: List[str], out_file: str,
                    out_file2: str) -> None:
        """计算每棵树的分支长度与支持值统计信息。

        替代原 ``tools.branchInfo`` 函数。
        """
        with open(out_file, "w") as f, open(out_file2, "w") as g:
            f.write("DS model_condition geneID medrootToLeafBrLen "
                     "avgrootToLeafBrLen maxrootToLeafBrLen stdrootToLeafBrLen "
                     "medtaxonToTaxonBrLen avgtaxonToTaxonBrLen "
                     "maxtaxonToTaxonBrLen stdtaxonToTaxonBrLen "
                     "medBrSupp avgBrSupp stdBrSupp\n")
            for gene in tree_files:
                r = os.path.basename(gene).split("-")
                mode = os.path.basename(os.path.dirname(gene))
                ds = r[0]
                trees = dendropy.TreeList.get(path=gene, schema="newick",
                                               rooting="force-rooted",
                                               preserve_underscores=True)
                for i, tree in enumerate(trees):
                    for m in tree.leaf_node_iter():
                        if m.edge.length is None:
                            m.edge.length = 0.0
                    dist_from_root = [n.distance_from_root()
                                      for n in tree.leaf_node_iter()]
                    br_len = TreeTools.leaf_to_leaf_distances(tree)
                    supp = TreeTools.branch_supports(tree, ds, mode, g)

                    med = TreeTools.median(sorted(dist_from_root))
                    max_br = max(dist_from_root)
                    avg = TreeTools.mean(dist_from_root)
                    std = TreeTools.pstdev(dist_from_root)

                    med2 = TreeTools.median(sorted(br_len))
                    max_br2 = max(br_len)
                    avg2 = TreeTools.mean(br_len)
                    std2 = TreeTools.pstdev(br_len)
                    avg_supp = TreeTools.mean(supp)
                    med_supp = TreeTools.median(sorted(supp))
                    std_supp = TreeTools.pstdev(supp)

                    f.write(f"{ds} {mode} {i+1} {med} {avg} {max_br} {std} "
                            f"{med2} {avg2} {max_br2} {std2} "
                            f"{med_supp} {avg_supp} {std_supp}\n")

    # ------------------------------------------------------------------
    # 占据率
    # ------------------------------------------------------------------
    @staticmethod
    def occupancy(search_pattern: str, out_file: str) -> None:
        """从 FASTA 比对文件计算占据率统计。

        替代原 ``tools.occupancy`` 函数。
        """
        search_files = glob.glob(search_pattern)
        if not search_files:
            print("No alignment files found! Please follow the structure "
                  "specified in the examples.")
            sys.exit(1)

        with open(out_file, "w") as g:
            for fname in search_files:
                fname = os.path.abspath(fname)
                base = os.path.basename(fname)
                gene_id = os.path.basename(os.path.dirname(fname))
                split_base = base.split("-")
                ds = split_base[0]
                model_cond = ("-".join(split_base[2:])).replace(".fasta", "")

                output = TreeTools.simplify_fasta(fname)
                taxon = ""
                for line in output.split("\n"):
                    if line.startswith(">"):
                        taxon = line[1:]
                        continue
                    if not line:
                        continue
                    new_line = re.sub("[N-]", "", line)
                    length = len(new_line)
                    g.write(f"{ds} {gene_id} {model_cond} {taxon} {length}\n")

    # ------------------------------------------------------------------
    # 文件合并
    # ------------------------------------------------------------------
    @staticmethod
    def concatenate_files(out_file: str, search_pattern: str) -> None:
        """将搜索模式匹配到的所有文件内容合并写入 out_file。"""
        search_files = glob.glob(search_pattern)
        if not search_files:
            print("No files found to concatenate!")
            sys.exit(1)
        with open(out_file, "a") as outfile:
            for fname in search_files:
                with open(fname) as infile:
                    for line in infile:
                        outfile.write(line)
