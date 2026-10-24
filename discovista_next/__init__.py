"""
DiscoVista-Next
===============

DiscoVista-Next 是原 DiscoVista（Discordance Visualization Tool）的 Python 3 全面重写版。

该包用于系统发育不一致性（discordance）的可视化与分析，完全用 Python 3 实现，
不再依赖 R 语言或其相关扩展包。

核心模块
--------
- ``discovista_next.core``      — 核心分析逻辑（树操作、进化支检测、GC统计、占据率）
- ``discovista_next.viz``       — 可视化模块（替代原 R 脚本的绘图功能）
- ``discovista_next.cli``       — 命令行接口
- ``discovista_next.gui``       — 基于 qt-material 的图形界面

作者: DiscoVista-Next 团队
许可证: GPL-3.0
"""

__version__ = "0.1.0"
__author__ = "DiscoVista-Next Team"
__license__ = "GPL-3.0"

# 分析模式常量
MODE_SPECIES_TREE = 0       # 物种树不一致性分析
MODE_GENE_TREE = 1          # 基因树不一致性分析
MODE_GC_CONTENT = 2         # GC含量分析
MODE_OCCUPANCY = 3          # 占据率分析
MODE_BRANCH_STAT = 4        # 分支支持 vs 分支长度分析
MODE_RELATIVE_FREQ = 5      # 相对频率分析

ALL_MODES = {
    MODE_SPECIES_TREE: "Species tree discordance",
    MODE_GENE_TREE: "Gene tree discordance",
    MODE_GC_CONTENT: "GC content analysis",
    MODE_OCCUPANCY: "Occupancy analysis",
    MODE_BRANCH_STAT: "Branch support vs branch length",
    MODE_RELATIVE_FREQ: "Relative frequency analysis",
}
