"""
GC 含量统计模块
===============

替代原 ``gc_stats.py``，计算 FASTA 比对文件中每个物种在不同密码子位置的
GC 含量（A、C、G、T 计数及比例）。
"""

import os
import re
import sys
from typing import Tuple


class GCStats:
    """GC 含量统计器。"""

    # 列名头部
    HEADER = (
        "GENE SEQUENCE TAXON "
        "A_C C_C G_C T_C N_C frag_C A_R C_R G_R T_R "
        "c1_A_C c1_C_C c1_G_C c1_T_C c1_N_C c1_frag_C c1_A_R c1_C_R c1_G_R c1_T_R "
        "c2_A_C c2_C_C c2_G_C c2_T_C c2_N_C c2_frag_C c2_A_R c2_C_R c2_G_R c2_T_R "
        "c3_A_C c3_C_C c3_G_C c3_T_C c3_N_C c3_frag_C c3_A_R c3_C_R c3_G_R c3_T_R"
    )

    # ------------------------------------------------------------------
    @staticmethod
    def _simplify_fasta(filename: str) -> str:
        """将多行 FASTA 压缩为单行序列格式。"""
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
    def _counts(seq: str) -> Tuple[int, int, int, int, int, int]:
        """统计序列中 a, c, g, t, n, gap 的数量。"""
        x = seq.lower()
        return (x.count("a"), x.count("c"), x.count("g"),
                x.count("t"), x.count("n"), x.count("-"))

    # ------------------------------------------------------------------
    @classmethod
    def process_alignment(cls, align_path: str) -> str:
        """处理单个 FASTA 比对文件，返回 gc-stat.txt 格式的字符串。

        Parameters
        ----------
        align_path : str
            FASTA 比对文件路径。

        Returns
        -------
        str
            统计结果文本。
        """
        src_fpath = os.path.abspath(align_path)
        if not os.path.exists(src_fpath):
            sys.stderr.write(f'Not found: "{src_fpath}"')
            return ""

        simplified = cls._simplify_fasta(src_fpath)
        gene = os.path.basename(os.path.dirname(src_fpath))

        lines_out = []
        seq = ""
        seq2 = ""

        for line in simplified.split("\n"):
            if line.startswith(">"):
                seq = line[1:]
                seq2 = seq.split("_")[0]
                continue
            if not line:
                continue

            a = [0, 0, 0, 0]
            c = [0, 0, 0, 0]
            g = [0, 0, 0, 0]
            t = [0, 0, 0, 0]
            n = [0, 0, 0, 0]
            d = [0, 0, 0, 0]

            (a[0], c[0], g[0], t[0], n[0], d[0]) = cls._counts(line)
            s = a[0] + c[0] + g[0] + t[0] + 0.0000000001
            sc = s / 3

            (a[1], c[1], g[1], t[1], n[1], d[1]) = cls._counts(line[0::3])
            (a[2], c[2], g[2], t[2], n[2], d[2]) = cls._counts(line[1::3])
            (a[3], c[3], g[3], t[3], n[3], d[3]) = cls._counts(line[2::3])

            try:
                row = (
                    f"{gene} {seq} {seq2} "
                    f"{a[0]} {c[0]} {g[0]} {t[0]} {n[0]} {d[0]} "
                    f"{a[0]/s} {c[0]/s} {g[0]/s} {t[0]/s} "
                    f"{a[1]} {c[1]} {g[1]} {t[1]} {n[1]} {d[1]} "
                    f"{a[1]/sc} {c[1]/sc} {g[1]/sc} {t[1]/sc} "
                    f"{a[2]} {c[2]} {g[2]} {t[2]} {n[2]} {d[2]} "
                    f"{a[2]/sc} {c[2]/sc} {g[2]/sc} {t[2]/sc} "
                    f"{a[3]} {c[3]} {g[3]} {t[3]} {n[3]} {d[3]} "
                    f"{a[3]/sc} {c[3]/sc} {g[3]/sc} {t[3]/sc}"
                )
                lines_out.append(row)
            except ZeroDivisionError:
                sys.stderr.write(f"{seq} {seq2} ERROR\n")
                sys.stderr.write(f"L:{line}*\n{s} {a}\n")

        return "\n".join(lines_out)

    # ------------------------------------------------------------------
    @classmethod
    def main(cls, align_path: str) -> None:
        """处理单个比对文件并将结果写入 gc-stat.txt。

        Parameters
        ----------
        align_path : str
            FASTA 比对文件路径。
        """
        result = cls.process_alignment(align_path)
        path = os.path.dirname(os.path.abspath(align_path))
        dest_fpath = os.path.join(path, "gc-stat.txt")
        with open(dest_fpath, "w") as dest:
            dest.write(result + "\n")

    # ------------------------------------------------------------------
    @classmethod
    def run_analysis(cls, search_pattern: str, out_file: str) -> int:
        """对所有匹配的比对文件执行 GC 统计并合并结果。

        Parameters
        ----------
        search_pattern : str
            FASTA 文件的 glob 模式。
        out_file : str
            合并后的 CSV 输出路径。

        Returns
        -------
        int
            处理的比对文件数量。
        """
        import glob as _glob
        search_files = _glob.glob(search_pattern)
        if not search_files:
            print("No alignment file found!")
            sys.exit(1)

        print(f"Number of alignments found: {len(search_files)}")

        for align in search_files:
            cls.main(align)
        print("All GC stat files have been generated")

        # 合并所有 gc-stat.txt
        with open(out_file, "w") as f:
            f.write(cls.HEADER.replace(" ", " ") + "\n")

        gc_search = os.path.join(os.path.dirname(os.path.dirname(
            search_files[0])), "*", "gc-stat.txt")
        # 更宽泛地搜索
        gc_search_pattern = search_pattern.rsplit("/", 1)[0] + "/*/gc-stat.txt"
        gc_files = _glob.glob(gc_search_pattern)

        # 回退到更简单的模式
        if not gc_files:
            base = os.path.dirname(search_files[0])
            gc_search2 = os.path.join(os.path.dirname(base), "*", "gc-stat.txt")
            gc_files = _glob.glob(gc_search2)

        from .tree_tools import TreeTools
        with open(out_file, "a") as outfile:
            for fname in gc_files:
                with open(fname) as infile:
                    for line in infile:
                        outfile.write(line)

        print(f"Concatenated GC stats written to {out_file}")
        return len(search_files)
