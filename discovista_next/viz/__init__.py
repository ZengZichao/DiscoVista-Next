"""DiscoVista-Next 可视化模块。

在导入时统一配置 matplotlib，确保在 frozen (PyInstaller) 环境下
也能正确生成图形。
"""

import matplotlib

# 使用 Agg 后端（非交互式后端，适合批量生成图形）
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

# ── 全局 matplotlib 配置 ──────────────────────────────────────────
# 确保字体大小合理、图形紧凑
plt.rcParams.update({
    "figure.dpi": 100,
    "savefig.dpi": 150,
    "font.size": 8,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "figure.autolayout": False,
    "pdf.fonttype": 42,        # TrueType 字体（保证 PDF 可编辑）
    "ps.fonttype": 42,
})

# 尝试设置支持中文的字体（如果系统可用）
for _font_name in (
    "Microsoft YaHei",   # Windows
    "SimHei",             # Windows
    "PingFang SC",        # macOS
    "WenQuanYi Micro Hei",  # Linux
    "Noto Sans CJK SC",   # Linux
    "DejaVu Sans",        # Fallback
):
    try:
        from matplotlib.font_manager import FontProperties, findfont
        fp = FontProperties(family=_font_name)
        path = findfont(fp)
        if path and "DejaVu" not in path:
            plt.rcParams["font.sans-serif"] = [_font_name] + plt.rcParams.get("font.sans-serif", [])
            plt.rcParams["axes.unicode_minus"] = False
            break
    except Exception:
        continue
else:
    # 如果没有找到中文字体，至少禁用 unicode minus
    plt.rcParams["axes.unicode_minus"] = False


from .depict_clades import DepictClades   # noqa: E402
from .gc_plot import GCPlot                # noqa: E402
from .occupancy_plot import OccupancyPlot  # noqa: E402
from .branch_stat_plot import BranchStatPlot  # noqa: E402
from .tree_plot import TreePlot            # noqa: E402
from .relative_freq_plot import RelativeFreqPlot  # noqa: E402

__all__ = [
    "DepictClades",
    "GCPlot",
    "OccupancyPlot",
    "BranchStatPlot",
    "TreePlot",
    "RelativeFreqPlot",
]
