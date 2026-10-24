"""
相对频率分析模块
================

替代原 ``map_names.py``、``spit-hypo-trees.py``、``display.py``、
``pos-for-hyp.sh`` 等多个脚本的功能，计算物种树中关键分支附近
四分体拓扑的相对频率。

注意：原版依赖 ASTRAL (DiscoVista 分支) 来计算四分体频率。
本模块假设 ASTRAL 的输出文件 ``freqQuad.csv`` 已经存在。
如需从基因树直接计算，请先运行 ASTRAL。
"""

import os
import re
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

import dendropy


class RelativeFrequency:
    """相对频率分析器。

    将 ASTRAL 四分体频率输出映射到进化支名称，
    并生成用于可视化的修正频率文件。
    """

    # ------------------------------------------------------------------
    def __init__(self, names_file: str, annotation_file: str,
                 freq_stat_file: str, out_file: str, tree_file: str):
        self.names_file = names_file
        self.annotation_file = annotation_file
        self.freq_stat_file = freq_stat_file
        self.out_file = out_file
        self.tree_file = tree_file

        self.out = open(out_file, "w")
        self.tree = dendropy.Tree.get(
            path=tree_file, schema="newick",
            rooting="force-rooted", preserve_underscores=True)
        self.tree.encode_bipartitions()

        self._set_edges_map()
        self._generate_clades_dict()
        self._map_clades_to_edges()

    # ------------------------------------------------------------------
    def _set_edges_map(self):
        """构建从物种集合到分支长度的映射。"""
        edge_map = {}
        all_taxa = {nd.taxon.label for nd in self.tree.leaf_nodes()}
        self.available_nodes = set()

        for nd in self.tree.postorder_node_iter():
            if nd.label is not None and not nd.is_leaf():
                self.available_nodes.add(nd.label)
            edge = nd.edge
            if edge.bipartition is not None:
                taxa_set = {t.label for t in
                            edge.bipartition.leafset_taxa(self.tree.taxon_namespace)}
                side1 = ",".join(sorted(taxa_set))
                side2 = ",".join(sorted(all_taxa - taxa_set))
                edge_map[side1] = edge.length
                edge_map[side2] = edge.length
        self.edge_map = edge_map

    # ------------------------------------------------------------------
    def _generate_clades_dict(self):
        """从注释文件构建物种→进化支和进化支→物种列表的映射。"""
        taxa_dict = {}
        all_clades = defaultdict(list)
        with open(self.annotation_file) as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) < 2:
                    continue
                taxon, clade = parts[0].strip(), parts[1].strip()
                taxa_dict[taxon] = clade
                all_clades[clade].append(taxon)
        self.taxa_dict = taxa_dict
        self.clades = dict(all_clades)

    # ------------------------------------------------------------------
    def _get_clades(self, bipart_quad: List[str]) -> List[List[str]]:
        """将四分体的物种集合映射为进化支名称集合。"""
        topology = []
        for quad in bipart_quad:
            quad_set = set(quad.split(", "))
            h = []
            while quad_set:
                y = list(quad_set)[0]
                if set(self.clades.get(self.taxa_dict.get(y, y), [])) \
                        .issubset(quad_set):
                    quad_set = quad_set - set(self.clades[self.taxa_dict[y]])
                    h.append(self.taxa_dict[y])
                else:
                    print(f"Couldn't map bipartition to clades. "
                          f"Check annotation file!")
                    sys.exit(1)
            topology.append(h)
        return topology

    # ------------------------------------------------------------------
    def _get_formatted_bipart(self, topology: List[str]) -> str:
        """将进化支拓扑格式化为以分支长度为键的字符串。"""
        quad0 = ",".join(sorted(topology[0]))
        quad0 = str(int(self.edge_map.get(quad0, 0)))
        quad1 = ",".join(sorted(topology[1]))
        quad1 = str(int(self.edge_map.get(quad1, 0)))
        if quad0 < quad1:
            return f"{quad0},{quad1}"
        else:
            return f"{quad1},{quad0}"

    # ------------------------------------------------------------------
    def _get_key_from_list_clades(self, topology1, topology2):
        f1 = self._get_formatted_bipart(topology1)
        f2 = self._get_formatted_bipart(topology2)
        if f1 < f2:
            return f"{f1} | {f2}"
        else:
            return f"{f2} | {f1}"

    # ------------------------------------------------------------------
    def _map_taxa_to_clades(self, line: str) -> Tuple[str, bool]:
        flag = True
        key = ""
        line_list = line.strip().split("\t")
        if len(line_list) < 3 or line_list[0] not in self.available_nodes:
            flag = False
            return key, flag

        bipartitions = line_list[2].split("#")
        bipart_quad1 = bipartitions[0].replace("}", "").replace("|", "") \
            .split("{")[1:3]
        bipart_quad2 = bipartitions[1].replace("}", "").replace("|", "") \
            .split("{")[1:3]
        topology1 = self._get_clades(bipart_quad1)
        topology2 = self._get_clades(bipart_quad2)
        key = self._get_key_from_list_clades(topology1, topology2)
        return key, flag

    # ------------------------------------------------------------------
    def _map_clades_to_edges(self):
        """将进化支映射到树上的边。"""
        tree = self.tree
        clade_to_edge = {}
        all_taxa = {l.taxon.label.replace("'", "")
                    for l in tree.leaf_nodes()}
        flag = 0

        for edge in tree.postorder_internal_edge_iter():
            taxa = edge.bipartition.leafset_taxa(tree.taxon_namespace)
            main_taxa = {l.label.replace("'", "") for l in taxa}
            main_other = all_taxa - main_taxa

            if (edge.head_node == tree.seed_node
                    or edge.tail_node == tree.seed_node):
                children = tree.seed_node.child_nodes()
                if (children[0].is_leaf() or children[1].is_leaf()
                        or flag == 1):
                    continue
                else:
                    e0 = [i for i in children[0].incident_edges()
                          if i.head_node is not tree.seed_node
                          or i.tail_node is not tree.seed_node]
                    e1 = [i for i in children[1].incident_edges()
                          if i.head_node is not tree.seed_node
                          or i.tail_node is not tree.seed_node]
                    neighbors = e0 + e1
                    flag = 1
            else:
                neighbors = edge.get_adjacent_edges()

            if len(neighbors) < 4:
                continue

            bipart1 = []
            bipart2 = []
            for e in neighbors:
                e_taxa = e.bipartition.leafset_taxa(tree.taxon_namespace)
                taxa_labels = sorted([l.label.replace("'", "")
                                       for l in e_taxa])
                other_side = sorted(list(all_taxa - set(taxa_labels)))
                if not taxa_labels or not other_side:
                    continue
                if set(taxa_labels).issubset(main_taxa):
                    bipart = ",".join(taxa_labels)
                    bipart1.append(str(int(self.edge_map.get(bipart, 0))))
                elif set(taxa_labels).issubset(main_other):
                    bipart = ",".join(taxa_labels)
                    bipart2.append(str(int(self.edge_map.get(bipart, 0))))
                elif set(other_side).issubset(main_taxa):
                    bipart = ",".join(other_side)
                    bipart1.append(str(int(self.edge_map.get(bipart, 0))))
                elif set(other_side).issubset(main_other):
                    bipart = ",".join(other_side)
                    bipart2.append(str(int(self.edge_map.get(bipart, 0))))

            if len(bipart1) < 2 or len(bipart2) < 2:
                continue

            bipart1_str = f"{min(bipart1[0], bipart1[1])},{max(bipart1[0], bipart1[1])}"
            bipart2_str = f"{min(bipart2[0], bipart2[1])},{max(bipart2[0], bipart2[1])}"

            if bipart1_str < bipart2_str:
                bipart_str = f"{bipart1_str} | {bipart2_str}"
            else:
                bipart_str = f"{bipart2_str} | {bipart1_str}"

            edge.label = bipart_str
            clade_to_edge[bipart_str] = edge

        self.clade_to_edge = clade_to_edge

    # ------------------------------------------------------------------
    def generate_new_freq_stat(self):
        """生成修正后的四分体频率统计文件。"""
        with open(self.freq_stat_file) as f:
            freq_stat = f.readlines()

        linet = []
        c = 0
        for i in range(len(freq_stat)):
            line = freq_stat[i]
            key, flag = self._map_taxa_to_clades(line)
            if not flag:
                continue
            if c % 3 == 0:
                node = str(int(self.clade_to_edge[key].length))
                if c > 0:
                    self.out.write("\t".join(linet[0]) + "\tt1\n")
                    if linet[1][2] < linet[2][2]:
                        self.out.write("\t".join(linet[1]) + "\tt2\n")
                        self.out.write("\t".join(linet[2]) + "\tt3\n")
                    else:
                        self.out.write("\t".join(linet[2]) + "\tt2\n")
                        self.out.write("\t".join(linet[1]) + "\tt3\n")
                    linet = []
                linet.append([line.strip("\n"), node, key])
                c += 1
            else:
                linet.append([line.strip("\n"), node, key])
                c += 1

        if linet:
            self.out.write("\t".join(linet[0]) + "\tt1\n")
            if linet[1][2] < linet[2][2]:
                self.out.write("\t".join(linet[1]) + "\tt2\n")
                self.out.write("\t".join(linet[2]) + "\tt3\n")
            else:
                self.out.write("\t".join(linet[2]) + "\tt2\n")
                self.out.write("\t".join(linet[1]) + "\tt3\n")
        self.out.close()

    # ------------------------------------------------------------------
    @classmethod
    def run(cls, data_path: str, annotation_file: str, names_file: str,
            out_dir: str, outgroup: str = "") -> str:
        """执行相对频率分析的完整流程。

        Parameters
        ----------
        data_path : str
            包含 ``estimated_species_tree.tree`` 和
            ``estimated_gene_trees.tree`` 的目录。
        annotation_file : str
            注释文件路径。
        names_file : str
            物种名称文件路径。
        out_dir : str
            输出目录路径。
        outgroup : str
            外群名称。

        Returns
        -------
        str
            输出目录路径。
        """
        species_tree = os.path.join(data_path, "estimated_species_tree.tree")
        gene_trees = os.path.join(data_path, "estimated_gene_trees.tree")

        if not os.path.exists(species_tree):
            print(f"Species tree not found: {species_tree}")
            sys.exit(1)
        if not os.path.exists(gene_trees):
            print(f"Gene trees not found: {gene_trees}")
            sys.exit(1)

        # 创建输出目录
        os.makedirs(out_dir, exist_ok=True)

        # 复制必要文件到输出目录
        import shutil
        out_species = os.path.join(out_dir, os.path.basename(species_tree))
        out_genes = os.path.join(out_dir, os.path.basename(gene_trees))
        shutil.copy2(species_tree, out_species)
        shutil.copy2(gene_trees, out_genes)

        # 查找 ASTRAL 输出的四分体频率文件
        freq_file = os.path.join(data_path, "freqQuad.csv")
        if not os.path.exists(freq_file):
            print(f"Warning: freqQuad.csv not found at {freq_file}")
            print("Please run ASTRAL (DiscoVista branch) first to generate "
                  "quartet frequencies.")
            return out_dir

        out_corrected = os.path.join(out_dir, "freqQuadCorrected.csv")
        rf = cls(names_file, annotation_file, freq_file,
                 out_corrected, out_species)
        rf.generate_new_freq_stat()

        return out_dir
