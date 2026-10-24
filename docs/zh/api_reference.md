# API 参考

## 模块概览

- [`discovista_next`](#discovista_next) — 顶层包
- [`discovista_next.core`](#discovista_nextcore) — 核心分析
- [`discovista_next.viz`](#discovista_nextviz) — 可视化
- [`discovista_next.cli`](#discovista_nextcli) — 命令行
- [`discovista_next.gui`](#discovista_nextgui) — 图形界面

---

## discovista_next

### 常量

#### `MODE_SPECIES_TREE = 0`
物种树不一致性分析模式。

#### `MODE_GENE_TREE = 1`
基因树不一致性分析模式。

#### `MODE_GC_CONTENT = 2`
GC 含量分析模式。

#### `MODE_OCCUPANCY = 3`
占据率分析模式。

#### `MODE_BRANCH_STAT = 4`
分支统计 vs 分支长度分析模式。

#### `MODE_RELATIVE_FREQ = 5`
相对频率分析模式。

#### `ALL_MODES: dict`
所有模式 ID 到名称的映射字典。

---

## discovista_next.core

### Options

```python
class Options:
    path: str
    mode: int
    annotation: str
    clades: str
    root: str
    threshold: float
    label: str
    model_cond: Optional[str]
    new_model: Optional[str]
    new_order: Optional[str]
    missing: int
    style: int
    outg: str
    names: str
    search: Optional[str]
    search_thr: Optional[str]
    search_rooted: Optional[str]
    search_thr_rooted: Optional[str]
```

#### `Options.from_args(argv=None) -> Options`
从命令行参数构建 Options 对象。

**参数**
- `argv` (list[str] | None): 命令行参数列表

**返回**
- `Options` 实例

#### `Options.multiplier -> float`
阈值乘数属性。若阈值 <= 1.0 则返回 100.0，否则返回 1.0。

---

### Analyzer

```python
class Analyzer:
    def __init__(self, opt: Options)
    def analyze(self) -> None
```

#### `Analyzer(opt)`
创建分析器实例。

**参数**
- `opt` (Options): 配置选项

#### `Analyzer.analyze()`
执行分析。根据 `opt.mode` 自动选择对应的分析方法。

---

### TreeTools

树操作工具类，所有方法均为静态方法。

#### `TreeTools.remove_edges_from_tree(tree_file, threshold, output_file=None)`
收缩树中低于阈值的分支。

#### `TreeTools.reroot(tree_file, root_def, annotation, if_print=1, results_file=None)`
根据根定义对树进行重根操作。

#### `TreeTools.branch_info(tree_files, out_file, out_file2)`
计算分支长度和支持值统计信息。

#### `TreeTools.occupancy(search_pattern, out_file)`
从 FASTA 比对文件计算占据率统计。

#### `TreeTools.concatenate_files(out_file, search_pattern)`
合并多个文件内容。

---

### CladeAnalyzer

```python
class CladeAnalyzer:
    def __init__(self, taxa: Set[str], out_file: str)
    def read_clades(self, filename: str) -> None
    def analyze(self, tree, tree_name, mult: float) -> None
```

#### `CladeAnalyzer.run(names_file, clades_file, out_file, mult, tree_files_str) -> None`
类方法，分析多棵树中的进化支单系性。

---

### GCStats

GC 含量统计器。

#### `GCStats.process_alignment(align_path) -> str`
处理单个 FASTA 比对文件，返回统计结果字符串。

#### `GCStats.main(align_path) -> None`
处理单个比对文件并写入 gc-stat.txt。

#### `GCStats.run_analysis(search_pattern, out_file) -> int`
对所有匹配文件执行 GC 统计并合并结果。

---

### Occupancy

占据率分析器。

#### `Occupancy.compute_occupancy(search_pattern, out_file) -> pd.DataFrame`
计算占据率数据并保存为 CSV。

#### `Occupancy.analyze(search_pattern, annotation_file, out_dir, model_cond=None)`
执行完整占据率分析。

---

### RelativeFrequency

相对频率分析器。

#### `RelativeFrequency.run(data_path, annotation_file, names_file, out_dir, outgroup="")`
执行相对频率分析的完整流程。

---

## discovista_next.viz

### DepictClades

进化支不一致性可视化器。

```python
class DepictClades:
    def __init__(self, out_dir, is_species_tree=True, missing_flag=0)
    def read_data(self, file_all, file_hs, clade_order=None,
                  new_clades=None, new_models=None) -> dict
    def plot_block(self, data, figure_size=(10.5, 12), page=1) -> None
    def plot_block_shades(self, data, figure_size=(10.5, 12)) -> None
    def plot_bargraphs(self, data, figure_size=(15, 19)) -> None
    def plot_bargraphs_proportion(self, data, figure_size=(15, 19)) -> None
    def plot_histograms(self, data, figure_size=(18, 18)) -> None
```

### GCPlot

GC 含量可视化器。

#### `GCPlot.run(gc_file) -> None`
执行完整的 GC 含量可视化。

### OccupancyPlot

占据率可视化器。

#### `OccupancyPlot.run(species_df, clades_df, max_g, single_model_df=None)`
执行完整的占据率可视化。

### BranchStatPlot

分支统计可视化器。

#### `BranchStatPlot.run(branch_stat_file, branch_support_file)`
执行完整的分支统计可视化。

### TreePlot

系统发育树可视化器。

#### `TreePlot.plot_tree(tree_file) -> str`
绘制树的多种视图到 PDF。

### RelativeFreqPlot

相对频率可视化器。

#### `RelativeFreqPlot.run(freq_file)`
执行完整的相对频率可视化。

---

## discovista_next.cli

#### `cli(argv=None) -> int`
命令行主函数。返回退出码 (0=成功, 1=失败)。

---

## discovista_next.gui

#### `main() -> int`
GUI 主入口函数。启动图形界面。

### i18n

#### `set_language(lang: str) -> None`
设置当前界面语言 (`"zh"` 或 `"en"`)。

#### `get_language() -> str`
获取当前界面语言。

#### `tr(key: str) -> str`
获取翻译文本。
