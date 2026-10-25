# DiscoVista-Next

**系统发育不一致性可视化与分析工具** — Python 3 全面重写版

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI](https://img.shields.io/pypi/v/discovista-next.svg)](https://pypi.org/project/discovista-next/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)]()
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23639011.svg)](https://doi.org/10.5281/zenodo.23639011)

[English](README.md) | **简体中文**

## 概述

DiscoVista-Next 是原 [DiscoVista](https://github.com/esayyari/DiscoVista)（Discordance Visualization Tool）的 Python 3 全面重写版本。原版由 Erfan Sayyari 和 Siavash Mirarab 编写，使用 Python 2 + R 混合架构。本版本将所有 R 依赖（ggplot2, reshape2, plyr, ape, optparse 等）全部改用 Python 3 实现，并新增了基于 qt-material 的图形用户界面。

## 主要特性

- **纯 Python 3**：不再依赖 R 语言或任何 R 扩展包
- **6 种分析模式**：物种树不一致性、基因树不一致性、GC 含量、占据率、分支统计、相对频率
- **完整可视化**：使用 matplotlib + seaborn 替代 ggplot2
- **图形界面**：基于 qt-material 的现代化 GUI，内置 26 个颜色主题
- **中英文切换**：支持中英文界面国际化
- **命令行工具**：保留 CLI 接口，兼容原版参数格式
- **自包含 exe**：可构建独立运行的 exe 文件，无需安装 Python 环境
- **示例数据**：随仓库提供 1KP 植物数据集的参数文件与获取脚本，方便快速上手

## 快速开始

### 安装

从 PyPI 安装（推荐终端用户）：

```bash
pip install discovista-next
```

从源码安装（推荐开发）：

```bash
# 克隆仓库
git clone https://github.com/ZengZichao/DiscoVista-Next.git
cd DiscoVista-Next

# 安装依赖
pip install -r requirements.txt

# 安装包（开发模式）
pip install -e .
```

### 命令行运行

```bash
# 物种树不一致性分析
discoVista -m 0 -c examples/1KP/parameters/clade-defs.txt \
    -p examples/1KP/species/ -t 95 -o results/

# 基因树不一致性分析
discoVista -m 1 -c examples/1KP/parameters/clade-defs.txt \
    -p examples/1KP/genetrees/filtered/ -t 95 -o results/

# GC 含量分析
discoVista -m 2 -p examples/1KP/GC/unfiltered/ -o results/

# 占据率分析
discoVista -m 3 -p examples/1KP/occupancy/filtered/ \
    -a examples/1KP/parameters/annotation.txt -o results/

# 分支统计 vs 分支长度
discoVista -m 4 -p examples/1KP/branchAnalysis/ \
    -r examples/1KP/parameters/rooting.txt \
    -a examples/1KP/parameters/annotation.txt -o results/

# 相对频率分析
discoVista -m 5 -p examples/1KP/relativeFreq/astral.trim50genes33taxa.no3rd.final-FNA2AA/ \
    -a examples/1KP/parameters/annotation.txt -o results/
```

### 启动 GUI

```bash
discoVista-gui
# 或
python -m discovista_next.gui.main
```

### 使用独立 exe

直接运行 `DiscoVista-Next.exe`，无需安装 Python。

1. 双击 `DiscoVista-Next.exe` 启动程序
2. 点击"加载示例数据"按钮自动填充所有参数路径
3. 选择分析模式，调整参数
4. 点击"运行分析"开始分析
5. 分析完成后，生成的图形将在右侧"绘图显示"面板中展示

### 构建 exe

```bash
python build_exe.py
# 或
pyinstaller DiscoVista-Next.spec
```

构建结果将出现在 `dist/DiscoVista-Next/` 目录下。

## 功能覆盖

DiscoVista-Next 完全覆盖原版 DiscoVista 的全部功能：

| 功能 | 原版 | DiscoVista-Next |
|------|------|----------------|
| 物种树不一致性分析 | ✅ | ✅ (模式 0) |
| 基因树不一致性分析 | ✅ | ✅ (模式 1) |
| GC 含量分析 | ✅ | ✅ (模式 2) |
| 占据率分析 | ✅ | ✅ (模式 3) |
| 分支统计 vs 分支长度 | ✅ | ✅ (模式 4) |
| 相对频率分析 | ✅ | ✅ (模式 5) |
| 进化支定义文件 | ✅ | ✅ |
| 注释文件 | ✅ | ✅ |
| 根定义文件 | ✅ | ✅ |
| 模型条件重排 | ✅ | ✅ |
| 进化支重排 | ✅ | ✅ |
| 缺失数据处理 | ✅ | ✅ |
| 图形用户界面 | ❌ | ✅ (26 个主题) |
| 中英文切换 | ❌ | ✅ |
| 独立 exe | ❌ | ✅ |
| 示例数据 | ✅ (需手动下载) | ✅ (随仓库提供) |

## 项目结构

```
DiscoVista-Next/
├── discovista_next/           # 主包
│   ├── __init__.py            # 包初始化，定义分析模式常量
│   ├── cli/                   # 命令行接口
│   │   └── main.py
│   ├── core/                  # 核心分析逻辑
│   │   ├── analyzer.py        # 分析控制器
│   │   ├── config.py          # 配置与选项处理
│   │   ├── find_clades.py     # 进化支单系性检测
│   │   ├── gc_stats.py        # GC 含量统计
│   │   ├── occupancy.py       # 占据率分析
│   │   ├── relative_freq.py   # 相对频率分析
│   │   └── tree_tools.py      # 树操作工具
│   ├── gui/                   # 图形界面
│   │   ├── main.py            # GUI 主窗口
│   │   ├── i18n.py            # 国际化
│   │   └── runtime_hook.py    # PyInstaller 运行时钩子
│   ├── resources/             # 图标等资源文件
│   └── viz/                   # 可视化模块
│       ├── depict_clades.py   # 进化支可视化
│       ├── gc_plot.py         # GC 含量绘图
│       ├── occupancy_plot.py  # 占据率绘图
│       ├── branch_stat_plot.py # 分支统计绘图
│       ├── tree_plot.py       # 系统发育树绘图
│       └── relative_freq_plot.py # 相对频率绘图
├── docs/                      # 文档
│   ├── en/                    # 英文文档
│   └── zh/                    # 中文文档
├── examples/1KP/              # 示例数据（参数文件 + 获取说明）
├── .github/workflows/         # CI：发布 Release 时自动上传 PyPI
├── build_exe.py               # PyInstaller 构建脚本
├── DiscoVista-Next.spec       # PyInstaller spec 文件
├── pyproject.toml             # 打包元数据与构建配置
├── CITATION.cff               # 引用元数据（GitHub / Zenodo）
├── requirements.txt           # Python 依赖
├── setup.py                   # 兼容旧工具链的入口（元数据在 pyproject.toml）
├── LICENSE                    # GPL-3.0 许可证
├── README.md                  # 英文说明
└── README.zh-CN.md            # 本文件（中文）
```

## 内置主题

DiscoVista-Next 包含 qt-material 的全部 26 个颜色主题：

- **暗色主题（9 个）**：Amber, Blue, Cyan, Lightgreen, Pink, Purple, Red, Teal, Yellow
- **亮色主题（17 个）**：Amber, Blue, Blue 500, Cyan, Cyan 500, Lightgreen, Lightgreen 500, Orange, Pink, Pink 500, Purple, Purple 500, Red, Red 500, Teal, Teal 500, Yellow

## 示例数据

仓库中的 `examples/1KP/` 收录了 1KP 植物数据集的参数文件：

- `parameters/annotation.txt` — 物种与进化支注释
- `parameters/clade-defs.txt` — 进化支（split）定义
- `parameters/rooting.txt` — 外群与定根定义
- `parameters/newModel.txt`、`parameters/newOrders.txt` — 模型条件与排序

基因树、序列比对、GC 含量、占据率等大体积数据（解压后约 400 MB）
不随仓库提供，需从原版 DiscoVista 仓库获取：

```bash
python examples/fetch_data.py
```

数据就绪后，在 GUI 中点击"加载示例数据"按钮即可自动填充所有参数路径。
详见 [示例数据说明](examples/README.md)。

## 文档导航

| 文档 | 说明 |
|------|------|
| [安装指南 (中文)](docs/zh/installation.md) | 详细安装步骤 |
| [使用手册 (中文)](docs/zh/user_guide.md) | 完整使用教程 |
| [开发者文档 (中文)](docs/zh/developer_guide.md) | 架构设计与开发指南 |
| [API 参考 (中文)](docs/zh/api_reference.md) | 完整 API 文档 |
| [FAQ (中文)](docs/zh/faq.md) | 常见问题解答 |
| [Installation Guide (English)](docs/en/installation.md) | 详细安装步骤 |
| [User Guide (English)](docs/en/user_guide.md) | 完整使用教程 |
| [Developer Guide (English)](docs/en/developer_guide.md) | 架构设计与开发指南 |
| [API Reference (English)](docs/en/api_reference.md) | 完整 API 文档 |
| [FAQ (English)](docs/en/faq.md) | 常见问题解答 |

## 开发

### 环境搭建

```bash
git clone https://github.com/ZengZichao/DiscoVista-Next.git
cd DiscoVista-Next
pip install -r requirements.txt
pip install -e .
```

### 构建 exe

```bash
python build_exe.py
```

## 已知问题与本地补丁

本版本在源码中以 `LOCAL PATCH 20261024-1` 标注了两处修复，缺一不可：

| 位置 | 问题 | 修复 |
|------|------|------|
| `discovista_next/viz/depict_clades.py` | 收缩树的单系状态列取错：`iloc[:, 3]` 取到的是进化支名而非 `MONO`，导致全部分类退化成 `Missing`，比例图随之崩溃 | 改取 `iloc[:, 2]`（`MONO` 列） |
| `requirements.txt`、`setup.py` | 读树代码在 `Tree.get()` / `TreeList.get()` 中共 6 处传入 `preserve_underscores`，该参数已从 dendropy 5.x 的公开签名中移除，仅剩未文档化的 `**kwargs` 透传（5.0.x 目前容忍，但不在受支持接口内） | 锁定 `dendropy==4.5.2`（流水线验证所用版本） |

分析结果文件的列顺序为 `ID  DS  MONO  BOOT  CLADE  BRANCHLEN`（由
`discovista_next/core/analyzer.py` 写出），上表的列索引即针对该顺序。

## 致谢

感谢 **杨智勇** 报告 `discovista_next/viz/depict_clades.py` 的列索引缺陷——该问题导致
全部分类退化为 `Missing`、比例图随之崩溃。本仓库 `LOCAL PATCH 20261024-1` 的修复即由
这次反馈促成，完整诊断与修复前后数据见
[issue #1](https://github.com/ZengZichao/DiscoVista-Next/issues/1)。

## 引用

如果您在研究中使用 DiscoVista-Next，请同时引用本软件及其所基于的原始论文。

**软件** —— 已归档至 Zenodo：

- 全部版本：[10.5281/zenodo.23639011](https://doi.org/10.5281/zenodo.23639011)
- 本次发布（v0.1.0）：[10.5281/zenodo.23639012](https://doi.org/10.5281/zenodo.23639012)

机器可读的引用元数据见 [CITATION.cff](CITATION.cff)，GitHub 的"Cite this repository"
按钮即读取该文件。

**原始论文**：

> Sayyari, E., Whitfield, J. B., & Mirarab, S. (2018). DiscoVista: Interpretable Visualizations of Gene Tree Discordance. *Molecular Phylogenetics and Evolution*, 122, 110-115.

## 许可证

[GPL-3.0](LICENSE)
