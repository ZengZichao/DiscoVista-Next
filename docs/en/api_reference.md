# API Reference

## Module Overview

- [`discovista_next`](#discovista_next) — Top-level package
- [`discovista_next.core`](#discovista_nextcore) — Core analysis
- [`discovista_next.viz`](#discovista_nextviz) — Visualization
- [`discovista_next.cli`](#discovista_nextcli) — Command-line interface
- [`discovista_next.gui`](#discovista_nextgui) — Graphical interface

---

## discovista_next

### Constants

#### `MODE_SPECIES_TREE = 0`
Species tree discordance analysis mode.

#### `MODE_GENE_TREE = 1`
Gene tree discordance analysis mode.

#### `MODE_GC_CONTENT = 2`
GC content analysis mode.

#### `MODE_OCCUPANCY = 3`
Occupancy analysis mode.

#### `MODE_BRANCH_STAT = 4`
Branch support vs branch length analysis mode.

#### `MODE_RELATIVE_FREQ = 5`
Relative frequency analysis mode.

#### `ALL_MODES: dict`
Mapping of all mode IDs to their names.

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
Build an Options object from command-line arguments.

**Parameters**
- `argv` (list[str] | None): Command-line argument list

**Returns**
- `Options` instance

#### `Options.multiplier -> float`
Threshold multiplier property. Returns 100.0 if threshold <= 1.0, else 1.0.

---

### Analyzer

```python
class Analyzer:
    def __init__(self, opt: Options)
    def analyze(self) -> None
```

#### `Analyzer(opt)`
Create an analyzer instance.

**Parameters**
- `opt` (Options): Configuration options

#### `Analyzer.analyze()`
Execute analysis. Automatically selects the correct method based on `opt.mode`.

---

### TreeTools

Tree operations utility class. All methods are static.

#### `TreeTools.remove_edges_from_tree(tree_file, threshold, output_file=None)`
Contract branches below the threshold in the tree.

#### `TreeTools.reroot(tree_file, root_def, annotation, if_print=1, results_file=None)`
Reroot the tree according to rooting definitions.

#### `TreeTools.branch_info(tree_files, out_file, out_file2)`
Compute branch length and support value statistics.

#### `TreeTools.occupancy(search_pattern, out_file)`
Compute occupancy statistics from FASTA alignment files.

#### `TreeTools.concatenate_files(out_file, search_pattern)`
Concatenate contents of multiple files.

---

### CladeAnalyzer

```python
class CladeAnalyzer:
    def __init__(self, taxa: Set[str], out_file: str)
    def read_clades(self, filename: str) -> None
    def analyze(self, tree, tree_name, mult: float) -> None
```

#### `CladeAnalyzer.run(names_file, clades_file, out_file, mult, tree_files_str) -> None`
Class method to analyze clade monophyly across multiple trees.

---

### GCStats

GC content statistics calculator.

#### `GCStats.process_alignment(align_path) -> str`
Process a single FASTA alignment file, returning statistics as a string.

#### `GCStats.main(align_path) -> None`
Process a single alignment file and write to gc-stat.txt.

#### `GCStats.run_analysis(search_pattern, out_file) -> int`
Run GC statistics on all matching files and merge results.

---

### Occupancy

Occupancy analysis calculator.

#### `Occupancy.compute_occupancy(search_pattern, out_file) -> pd.DataFrame`
Compute occupancy data and save as CSV.

#### `Occupancy.analyze(search_pattern, annotation_file, out_dir, model_cond=None)`
Execute complete occupancy analysis.

---

### RelativeFrequency

Relative frequency analyzer.

#### `RelativeFrequency.run(data_path, annotation_file, names_file, out_dir, outgroup="")`
Execute the complete relative frequency analysis workflow.

---

## discovista_next.viz

### DepictClades

Clade discordance visualizer.

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

GC content visualizer.

#### `GCPlot.run(gc_file) -> None`
Execute complete GC content visualization.

### OccupancyPlot

Occupancy visualizer.

#### `OccupancyPlot.run(species_df, clades_df, max_g, single_model_df=None)`
Execute complete occupancy visualization.

### BranchStatPlot

Branch statistics visualizer.

#### `BranchStatPlot.run(branch_stat_file, branch_support_file)`
Execute complete branch statistics visualization.

### TreePlot

Phylogenetic tree visualizer.

#### `TreePlot.plot_tree(tree_file) -> str`
Draw multiple tree views to a PDF.

### RelativeFreqPlot

Relative frequency visualizer.

#### `RelativeFreqPlot.run(freq_file)`
Execute complete relative frequency visualization.

---

## discovista_next.cli

#### `cli(argv=None) -> int`
Command-line main function. Returns exit code (0=success, 1=failure).

---

## discovista_next.gui

#### `main() -> int`
GUI main entry function. Launches the graphical interface.

### i18n

#### `set_language(lang: str) -> None`
Set the current interface language (`"zh"` or `"en"`).

#### `get_language() -> str`
Get the current interface language.

#### `tr(key: str) -> str`
Get translated text for the given key.
