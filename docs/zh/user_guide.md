# DiscoVista-Next 使用手册

## 1. 概述

DiscoVista-Next 是原 [DiscoVista](https://github.com/esayyari/DiscoVista)（Discordance Visualization Tool）的 Python 3 全面重写版本。它是一个用于系统发育不一致性（discordance）可视化与分析的工具，完全用 Python 3 实现，不再依赖 R 语言或其相关扩展包。

### 1.1 主要特性

- **纯 Python 3**：不再依赖 R 语言或任何 R 扩展包
- **6 种分析模式**：物种树不一致性、基因树不一致性、GC 含量、占据率、分支统计、相对频率
- **完整可视化**：使用 matplotlib + seaborn 替代 ggplot2，生成高质量 PDF 图表
- **图形界面**：基于 qt-material 的现代化 GUI，内置 26 个颜色主题
- **中英文切换**：支持中英文界面国际化
- **命令行工具**：保留 CLI 接口，兼容原版参数格式
- **自包含 exe**：可构建独立运行的 exe 文件，无需安装 Python 环境
- **示例数据**：1KP 参数文件随仓库提供，大体积数据文件需按 `examples/README.md` 的说明单独获取

### 1.2 分析模式

| 模式 | 名称 | 说明 |
|------|------|------|
| 0 | 物种树不一致性分析 | 分析物种树中预定义进化支的支持状态 |
| 1 | 基因树不一致性分析 | 分析基因树中进化支的单系性 |
| 2 | GC 含量分析 | 计算各物种在不同密码子位置的 GC 含量 |
| 3 | 占据率分析 | 统计物种在各基因中的序列占据率 |
| 4 | 分支统计 vs 分支长度 | 分析分支支持与分支长度的关系 |
| 5 | 相对频率分析 | 计算关键分支附近的四分体拓扑频率 |

---

## 2. 安装

### 2.1 从源代码安装

```bash
# 进入项目目录
cd DiscoVista-Next-项目代码

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 安装依赖和本包
pip install -e .
```

### 2.2 验证安装

```bash
# 命令行工具
discoVista --help

# 启动 GUI
discoVista-gui
```

### 2.3 使用独立 exe 文件

如果您获得了 `DiscoVista-Next.exe` 文件，无需安装 Python 环境，直接双击即可运行 GUI 界面。

---

## 3. 构建独立 exe 文件

### 3.1 前提条件

```bash
pip install pyinstaller
pip install -e .
```

### 3.2 构建方法一：使用脚本

```bash
python build_exe.py
```

### 3.3 构建方法二：使用 spec 文件

```bash
pyinstaller DiscoVista-Next.spec
```

### 3.4 构建结果

构建完成后，独立 exe 文件位于 `dist/DiscoVista-Next.exe`。

### 3.5 注意事项

- exe 文件包含所有依赖（PySide6、matplotlib、dendropy 等），不含示例数据，文件约 200-400MB
- 首次启动可能较慢（解压临时文件）
- 确保 `examples/` 目录存在且包含示例数据

---

## 4. 输入文件格式

### 4.1 注释文件（annotation file）

Tab 分隔，每行包含物种名和所属进化支名：

```
Species_A	Clade_1
Species_B	Clade_1
Species_C	Clade_2
```

**用途**：模式 3（占据率分析）和模式 5（相对频率分析）需要此文件。

### 4.2 进化支定义文件（clade definition file）

Tab 分隔，各列含义如下：

| 列名 | 说明 |
|------|------|
| Clade Name | 进化支名称 |
| Clade Definition | 进化支定义（用 + 或 - 组合已有进化支或物种） |
| Section Letter | 分组字母（用于排序和分组显示） |
| Components | 关键组成部分（若某组成部分完全缺失则该进化支标记为缺失） |
| Show | 0/1（是否在图中显示） |
| Comments | 备注 |

**注意**：必须定义名为 `All` 的进化支，包含所有物种（设 Show=0）。

示例（来自 1KP 数据集）：

```
Clade Name	Clade Definition	Section Letter	Components	Show	Comments
All	SpeciesA+SpeciesB+SpeciesC+...	None	None	0	All species
Landplants	All-Base	None	Base+Charales+Coleochaetales+Zygnematophyceae	1	Land plants
Base	Base1+Base2	None	None	1	Basal species
```

### 4.3 根定义文件（rooting file）

每行一组外群物种（空格分隔），第一行为最远的外群：

```
Outgroup_Species_1 Outgroup_Species_2
Outgroup_Species_3
```

**用途**：模式 4（分支统计）需要此文件。

### 4.4 模型条件重排文件（new model file）

Tab 分隔，两行：
- 第一行：原始模型条件名称（按显示顺序）
- 第二行：新的模型条件名称（与第一行对应）

### 4.5 进化支重排文件（new order file）

Tab 分隔，两行：
- 第一行：原始进化支名称（按期望显示顺序）
- 第二行：新的进化支名称（与第一行对应）

---

## 5. 数据目录结构

每种分析模式需要不同的数据目录结构。

### 5.1 物种树（模式 0）

```
data/
├── ModelCondition1-DST/
│   └── estimated_species_tree.tree
├── ModelCondition2-DST/
│   └── estimated_species_tree.tree
└── ModelCondition3-DST/
    └── estimated_species_tree.tree
```

说明：
- `ModelCondition` 是分析方法/条件的名称（如 `RAxML_highly_filtered`）
- `DST` 是数据序列类型（如 `FNA2AA`）
- 文件名必须为 `estimated_species_tree.tree`
- Newick 格式，支持值标注在内部节点上

### 5.2 基因树（模式 1）

```
data/
├── GeneID1/
│   ├── GeneID1-ModelCondition1-DST/
│   │   └── estimated_gene_trees.tree
│   └── GeneID1-ModelCondition2-DST/
│       └── estimated_gene_trees.tree
├── GeneID2/
│   ├── GeneID2-ModelCondition1-DST/
│   │   └── estimated_gene_trees.tree
│   └── GeneID2-ModelCondition2-DST/
│       └── estimated_gene_trees.tree
```

说明：
- 第一级目录是基因 ID
- 第二级目录格式为 `GeneID-ModelCondition-DST`
- 文件名必须为 `estimated_gene_trees.tree`

### 5.3 GC 含量（模式 2）

```
data/
├── GeneID1/
│   └── DST-alignment-noFilter.fasta
├── GeneID2/
│   └── DST-alignment-noFilter.fasta
```

说明：
- 第一级目录是基因 ID
- 文件名格式为 `DST-alignment-noFilter.fasta`（如 `FNA2AA-alignment-noFilter.fasta`）

### 5.4 占据率（模式 3）

```
data/
├── GeneID1/
│   ├── DST-alignment-ModelCondition1.fasta
│   └── DST-alignment-ModelCondition2.fasta
├── GeneID2/
│   ├── DST-alignment-ModelCondition1.fasta
│   └── DST-alignment-ModelCondition2.fasta
```

说明：
- 文件名格式为 `DST-alignment-ModelCondition.fasta`

### 5.5 分支统计（模式 4）

```
data/
├── ModelCondition1/
│   └── DST-estimated_gene_trees.tree
├── ModelCondition2/
│   └── DST-estimated_gene_trees.tree
```

说明：
- 第一级目录是模型条件名称
- 文件名格式为 `DST-estimated_gene_trees.tree`
- 每个文件包含多棵基因树（Newick 格式，每行一棵）

### 5.6 相对频率（模式 5）

```
data/
├── estimated_species_tree.tree
├── estimated_gene_trees.tree
└── freqQuad.csv  (ASTRAL 输出)
```

说明：
- `estimated_species_tree.tree`：物种树（Newick 格式）
- `estimated_gene_trees.tree`：所有基因树合并在一个文件中
- `freqQuad.csv`：由 ASTRAL（DiscoVista 分支）生成的四分体频率文件

**注意**：模式 5 需要先运行 ASTRAL 生成 `freqQuad.csv`。

---

## 6. 命令行使用

### 6.1 基本语法

```bash
discoVista [options]
```

### 6.2 参数说明

| 参数 | 全名 | 说明 |
|------|------|------|
| `-m` | `--mode` | 分析模式 (0-5) |
| `-p` | `--path` | 数据目录路径 |
| `-o` | `--output` | 输出目录路径 |
| `-a` | `--annotation` | 注释文件路径 |
| `-c` | `--clades` | 进化支定义文件路径 |
| `-r` | `--rooting` | 根定义文件路径 |
| `-t` | `--threshold` | 自展支持阈值 |
| `-x` | `--modelCond` | 单一模型条件（占据率分析） |
| `-y` | | 模型条件重排文件 |
| `-w` | | 进化支重排文件 |
| `-k` | `--missing` | 缺失数据标志 (1=部分缺失视为完整) |
| `-g` | `--outgroup` | 外群名称（相对频率分析） |
| `-s` | `--style` | 颜色样式集 |

### 6.3 命令示例

#### 6.3.1 物种树不一致性分析

```bash
discoVista -m 0 -c examples/1KP/parameters/clade-defs.txt \
    -p examples/1KP/species/ -t 95 \
    -y examples/1KP/parameters/newModel.txt \
    -w examples/1KP/parameters/newOrders.txt \
    -o examples/1KP/results
```

#### 6.3.2 基因树不一致性分析

```bash
discoVista -m 1 -c examples/1KP/parameters/clade-defs.txt \
    -p examples/1KP/genetrees/filtered/ -t 75 \
    -y examples/1KP/parameters/newModel.txt \
    -w examples/1KP/parameters/newOrders.txt \
    -o examples/1KP/results
```

#### 6.3.3 GC 含量分析

```bash
discoVista -m 2 -p examples/1KP/GC/unfiltered/ \
    -o examples/1KP/results
```

#### 6.3.4 占据率分析

```bash
discoVista -m 3 -a examples/1KP/parameters/annotation.txt \
    -p examples/1KP/occupancy/filtered/ \
    -o examples/1KP/results
```

#### 6.3.5 分支统计 vs 分支长度

```bash
discoVista -m 4 -p examples/1KP/branchAnalysis/ \
    -r examples/1KP/parameters/rooting.txt \
    -o examples/1KP/results
```

#### 6.3.6 相对频率分析

```bash
discoVista -m 5 \
    -a examples/1KP/parameters/annotation-1.txt \
    -p examples/1KP/relativeFreq/astral.trim50genes33taxa.no3rd.final-FNA2AA/ \
    -o examples/1KP/results/anot1 -g Base
```

### 6.4 阈值说明

- **物种树分析（模式 0）**：通常使用 95（自展支持）或 0.95（本地后验概率）
- **基因树分析（模式 1）**：通常使用 75
- 当阈值 ≤ 1.0 时，自动乘以 100 转换为百分比

---

## 7. GUI 使用

### 7.1 启动 GUI

```bash
discoVista-gui
```

或直接运行 `DiscoVista-Next.exe`。

### 7.2 界面布局

主界面从上到下分为以下区域：

1. **顶部区域**：
   - **分析模式**：下拉菜单选择 6 种分析模式之一
   - **主题选择**：下拉菜单选择 26 个 qt-material 颜色主题之一

2. **参数设置区域**（可滚动）：
   - 数据目录路径 + 浏览按钮
   - 注释文件路径 + 浏览按钮
   - 进化支定义文件路径 + 浏览按钮
   - 根定义文件路径 + 浏览按钮
   - 自展阈值（数值输入框）
   - 输出目录路径 + 浏览按钮
   - 模型条件（文本输入）
   - 模型重排文件路径 + 浏览按钮
   - 进化支重排文件路径 + 浏览按钮
   - 缺失数据标志（复选框）
   - 外群名称（文本输入）

3. **操作按钮**：
   - **加载示例数据**：自动填充示例数据路径
   - **运行分析**：开始执行分析
   - **清空**：清空日志输出

4. **进度条**：分析运行时显示

5. **运行日志**：显示分析过程中的输出信息

6. **状态栏**：显示当前状态

### 7.3 主题选择

DiscoVista-Next 内置了 qt-material 库的所有 26 个颜色主题：

**暗色主题（9 个）：**
- Dark - Amber
- Dark - Blue
- Dark - Cyan
- Dark - Lightgreen
- Dark - Pink
- Dark - Purple
- Dark - Red
- Dark - Teal（默认）
- Dark - Yellow

**亮色主题（17 个）：**
- Light - Amber
- Light - Blue
- Light - Blue 500
- Light - Cyan
- Light - Cyan 500
- Light - Lightgreen
- Light - Lightgreen 500
- Light - Orange
- Light - Pink
- Light - Pink 500
- Light - Purple
- Light - Purple 500
- Light - Red
- Light - Red 500
- Light - Teal
- Light - Teal 500
- Light - Yellow

切换方式：
1. **下拉菜单**：在界面顶部的主题下拉框直接选择
2. **菜单栏**：视图 → 主题 → 选择对应主题

### 7.4 语言切换

- **菜单栏 → 语言 → 中文**：切换到中文界面
- **菜单栏 → 语言 → English**：切换到英文界面

### 7.5 加载示例数据

1. 点击"加载示例数据"按钮
2. 系统自动查找示例数据目录并填充以下参数：
   - 注释文件路径
   - 进化支定义文件路径
   - 根定义文件路径
   - 模型重排文件路径
   - 进化支重排文件路径
   - 数据目录路径（species 目录）
   - 输出目录路径
   - 分析模式设为 0（物种树分析）
   - 阈值设为 95
3. 可根据需要调整参数后点击"运行分析"

### 7.6 运行分析

1. 选择分析模式
2. 填写必填参数（数据路径、输出目录为必填）
3. 根据分析模式填写可选参数：
   - 模式 0、1：需要进化支定义文件和阈值
   - 模式 3、5：需要注释文件
   - 模式 4：需要根定义文件
4. 点击"运行分析"按钮
5. 观察进度条和日志输出
6. 分析完成后弹出成功提示，结果保存在输出目录

---

## 8. 输出文件说明

### 8.1 物种树/基因树分析（模式 0、1）

| 文件 | 说明 |
|------|------|
| `clades.txt` | 进化支分析原始结果（所有分支） |
| `clades.hs.txt` | 进化支分析原始结果（高支持分支） |
| `clades.txt.res` | 进化支分析结果（标准格式） |
| `clades.hs.txt.res` | 进化支分析结果（高支持，标准格式） |
| `*.block.pdf` | 分类热图（物种树） |
| `*.block-shades.pdf` | 支持值渐变热图（物种树） |
| `Monophyletic_Bargraphs.pdf` | 基因树条形图（计数） |
| `Monophyletic_Bargraphs_Porportion.pdf` | 基因树比例条形图 |
| `Monophyletic_Bootstrap_Support_2.pdf` | 自展支持分布直方图 |
| `finegrained/` | 细粒度结果目录 |

### 8.2 GC 含量分析（模式 2）

| 文件 | 说明 |
|------|------|
| `gc-stat.csv` | GC 统计数据 |
| `pTpP_GC_point.pdf` | GC 含量散点图 |
| `pTpP_GC_boxplot.pdf` | GC 含量箱线图 |

### 8.3 占据率分析（模式 3）

| 文件 | 说明 |
|------|------|
| `occupancy.csv` | 原始占据率数据 |
| `occupancy-final.csv` | 物种级统计 |
| `occupancy-clades-final.csv` | 进化支级统计 |
| `occupancy.pdf` | 物种占据率折线图 |
| `occupancy_clades.pdf` | 进化支占据率折线图 |
| `occupancy_map.pdf` | 单一模型条件热图（使用 -x 参数时） |

### 8.4 分支统计（模式 4）

| 文件 | 说明 |
|------|------|
| `branchStats.csv` | 分支统计（长度、支持值等） |
| `branchSupport.csv` | 分支支持值 |
| `histogram_MLBS_distribution.pdf` | MLBS 分布直方图 |
| `average_taxa_distance_vs_MLBS.pdf` | 平均距离 vs 支持值 |
| `maximum_taxa_distance_vs_MLBS.pdf` | 最大距离 vs 支持值 |

### 8.5 相对频率分析（模式 5）

| 文件 | 说明 |
|------|------|
| `freqQuadCorrected.csv` | 修正后的四分体频率 |
| `relativeFreq.pdf` | 相对频率图 |
| `tree.pdf` | 物种树可视化（矩形、径向） |

---

## 9. 示例数据说明

DiscoVista-Next 提供了 1KP 植物数据集作为示例数据，位于 `examples/1KP/` 目录下。

### 9.1 目录结构

```
examples/1KP/
├── parameters/           # 参数文件
│   ├── annotation.txt    # 主注释文件
│   ├── annotation-1.txt  # 假设1注释文件
│   ├── annotation-2.txt  # 假设2注释文件
│   ├── annotation-3.txt  # 假设3注释文件
│   ├── annotation-4.txt  # 假设4注释文件
│   ├── clade-defs.txt    # 进化支定义文件
│   ├── names.txt         # 物种名称列表
│   ├── newModel.txt      # 模型条件重排文件
│   ├── newOrders.txt     # 进化支重排文件
│   ├── rooting.txt       # 根定义文件
│   └── README            # 说明文件
├── species/              # 物种树数据
├── genetrees/            # 基因树数据
├── GC/                   # GC 含量分析数据
├── occupancy/            # 占据率分析数据
├── branchAnalysis/       # 分支统计数据
└── relativeFreq/         # 相对频率数据
```

### 9.2 快速开始

使用 GUI 的"加载示例数据"按钮，系统会自动：
1. 设置数据路径为 `species/` 目录
2. 设置所有参数文件路径
3. 设置分析模式为 0（物种树分析）
4. 设置阈值为 95

点击"运行分析"即可看到物种树不一致性分析的结果。

---

## 10. 高级用法

### 10.1 自定义进化支定义

您可以创建自己的进化支定义文件来定义感兴趣的进化支。请参考 `examples/1KP/parameters/clade-defs.txt` 的格式。

### 10.2 重排模型条件和进化支顺序

使用 `-y` 和 `-w` 参数可以重新排序图表中的模型条件和进化支显示顺序，使图表更易读。

### 10.3 缺失数据处理

使用 `-k 1` 参数可以将部分缺失的进化支视为完整进化支。这在某些物种的序列数据不完整时有用。

### 10.4 单一模型条件占据率图

使用 `-x MODEL_CONDITION` 参数可以为指定的模型条件生成占据率热图。

### 10.5 相对频率分析的前置步骤

模式 5 需要先运行 ASTRAL（DiscoVista 分支）生成 `freqQuad.csv` 文件：

```bash
java -jar astral.5.6.1.jar -i gene_trees.tre -q species_tree.tre -o freqQuad.csv
```

---

## 11. 主题列表

DiscoVista-Next 内置了 qt-material 的全部 26 个颜色主题。每种主题提供不同的主色调和辅助色搭配。

| 主题类型 | 主题名称 | 主色调 |
|---------|---------|--------|
| Dark | Amber | 琥珀色 |
| Dark | Blue | 蓝色 |
| Dark | Cyan | 青色 |
| Dark | Lightgreen | 浅绿色 |
| Dark | Pink | 粉色 |
| Dark | Purple | 紫色 |
| Dark | Red | 红色 |
| Dark | Teal | 青蓝色（默认） |
| Dark | Yellow | 黄色 |
| Light | Amber | 琥珀色 |
| Light | Blue | 蓝色 |
| Light | Blue 500 | 深蓝色 |
| Light | Cyan | 青色 |
| Light | Cyan 500 | 深青色 |
| Light | Lightgreen | 浅绿色 |
| Light | Lightgreen 500 | 深浅绿色 |
| Light | Orange | 橙色 |
| Light | Pink | 粉色 |
| Light | Pink 500 | 深粉色 |
| Light | Purple | 紫色 |
| Light | Purple 500 | 深紫色 |
| Light | Red | 红色 |
| Light | Red 500 | 深红色 |
| Light | Teal | 青蓝色 |
| Light | Teal 500 | 深青蓝色 |
| Light | Yellow | 黄色 |

---

## 12. 故障排除

### 12.1 常见问题

**Q: GUI 启动时出现黑屏或白屏？**

A: 尝试更新 qt-material：`pip install --upgrade qt-material`

**Q: 输出目录中只有 CSV 文件没有 PDF 图表？**

A: 检查 matplotlib 和 seaborn 是否正确安装，日志中是否有绘图相关错误。

**Q: 相对频率分析（模式 5）报错？**

A: 确保已运行 ASTRAL 生成 `freqQuad.csv` 文件并放置在数据目录中。

**Q: exe 文件启动很慢？**

A: 首次启动需要解压临时文件，后续启动会更快。

**Q: 提示"No tree found"?**

A: 检查数据目录结构是否符合要求（参见第 5 节）。

### 12.2 获取帮助

- 查看运行日志中的错误信息
- 使用 `--help` 查看命令行参数说明
- 确保数据目录结构符合要求
- 确保所有必填参数已正确设置

---

## 13. 引用

如果您在研究中使用 DiscoVista-Next，请引用原始论文：

> Sayyari, E., Whitfield, J. B., & Mirarab, S. (2018). DiscoVista: Interpretable Visualizations of Gene Tree Discordance. *Molecular Phylogenetics and Evolution*, 122, 110-115.
