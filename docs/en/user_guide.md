# DiscoVista-Next User Guide

## 1. Overview

DiscoVista-Next is a complete Python 3 rewrite of the original [DiscoVista](https://github.com/esayyari/DiscoVista) (Discordance Visualization Tool). It is a tool for visualizing and analyzing phylogenetic discordance, fully implemented in Python 3 without any R language dependencies.

### 1.1 Key Features

- **Pure Python 3**: No R language or R package dependencies
- **6 Analysis Modes**: Species tree discordance, gene tree discordance, GC content, occupancy, branch statistics, relative frequency
- **Complete Visualization**: Uses matplotlib + seaborn to replace ggplot2
- **Graphical Interface**: Modern GUI based on qt-material with 26 built-in color themes
- **Internationalization**: Chinese and English interface switching
- **CLI Tool**: Compatible with original command-line parameter format
- **Standalone EXE**: Can be built as a self-contained executable
- **Example Data**: 1KP parameter files ship with the repository; the large data files are downloaded separately (see `examples/README.md`)

### 1.2 Analysis Modes

| Mode | Name | Description |
|------|------|-------------|
| 0 | Species tree discordance | Analyze support status of predefined clades in species trees |
| 1 | Gene tree discordance | Analyze monophyly of clades in gene trees |
| 2 | GC content analysis | Calculate GC content at different codon positions |
| 3 | Occupancy analysis | Calculate sequence occupancy of species across genes |
| 4 | Branch support vs branch length | Analyze relationship between branch support and length |
| 5 | Relative frequency analysis | Calculate quartet topology frequencies near focal branches |

---

## 2. Installation

### 2.1 Install from Source

```bash
# Navigate to project directory
cd DiscoVista-Next-项目代码

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies and package
pip install -e .
```

### 2.2 Verify Installation

```bash
# CLI tool
discoVista --help

# Launch GUI
discoVista-gui
```

### 2.3 Using Standalone EXE

If you have obtained the `DiscoVista-Next.exe` file, simply double-click to run the GUI without installing Python.

---

## 3. Building Standalone EXE

### 3.1 Prerequisites

```bash
pip install pyinstaller
pip install -e .
```

### 3.2 Method 1: Using Build Script

```bash
python build_exe.py
```

### 3.3 Method 2: Using Spec File

```bash
pyinstaller DiscoVista-Next.spec
```

### 3.4 Build Output

The standalone exe file will be at `dist/DiscoVista-Next.exe`.

### 3.5 Notes

- The exe file includes all dependencies (~200-400MB); example data is not bundled
- First launch may be slow (extracting temporary files)
- Ensure `examples/` directory exists with example data

---

## 4. Input File Formats

### 4.1 Annotation File

Tab-separated, one line per species with clade name:

```
Species_A	Clade_1
Species_B	Clade_1
Species_C	Clade_2
```

**Used by**: Mode 3 (occupancy) and Mode 5 (relative frequency).

### 4.2 Clade Definition File

Tab-separated with the following columns:

| Column | Description |
|--------|-------------|
| Clade Name | Name of the clade |
| Clade Definition | Definition using + or - to combine species/clades |
| Section Letter | Grouping letter for sorting |
| Components | Key components (clade marked missing if any is absent) |
| Show | 0/1 (whether to show in plots) |
| Comments | Free-form comments |

**Note**: You must define a clade named `All` containing all species (set Show=0).

### 4.3 Rooting File

One line per outgroup group (space-separated), first line = most distant:

```
Outgroup_Species_1 Outgroup_Species_2
Outgroup_Species_3
```

**Used by**: Mode 4 (branch statistics).

### 4.4 Model Reorder File

Tab-separated, two lines:
- Line 1: Original model condition names (in display order)
- Line 2: New model condition names (corresponding to line 1)

### 4.5 Clade Reorder File

Tab-separated, two lines:
- Line 1: Original clade names (in desired display order)
- Line 2: New clade names (corresponding to line 1)

---

## 5. Data Directory Structure

### 5.1 Species Trees (Mode 0)

```
data/
├── ModelCondition1-DST/
│   └── estimated_species_tree.tree
├── ModelCondition2-DST/
│   └── estimated_species_tree.tree
```

### 5.2 Gene Trees (Mode 1)

```
data/
├── GeneID1/
│   ├── GeneID1-ModelCondition1-DST/
│   │   └── estimated_gene_trees.tree
│   └── GeneID1-ModelCondition2-DST/
│       └── estimated_gene_trees.tree
```

### 5.3 GC Content (Mode 2)

```
data/
├── GeneID1/
│   └── DST-alignment-noFilter.fasta
├── GeneID2/
│   └── DST-alignment-noFilter.fasta
```

### 5.4 Occupancy (Mode 3)

```
data/
├── GeneID1/
│   ├── DST-alignment-ModelCondition1.fasta
│   └── DST-alignment-ModelCondition2.fasta
```

### 5.5 Branch Analysis (Mode 4)

```
data/
├── ModelCondition1/
│   └── DST-estimated_gene_trees.tree
├── ModelCondition2/
│   └── DST-estimated_gene_trees.tree
```

### 5.6 Relative Frequency (Mode 5)

```
data/
├── estimated_species_tree.tree
├── estimated_gene_trees.tree
└── freqQuad.csv  (ASTRAL output)
```

**Note**: Mode 5 requires running ASTRAL first to generate `freqQuad.csv`.

---

## 6. Command Line Usage

### 6.1 Basic Syntax

```bash
discoVista [options]
```

### 6.2 Parameters

| Parameter | Long form | Description |
|-----------|-----------|-------------|
| `-m` | `--mode` | Analysis mode (0-5) |
| `-p` | `--path` | Data directory path |
| `-o` | `--output` | Output directory path |
| `-a` | `--annotation` | Annotation file path |
| `-c` | `--clades` | Clade definition file path |
| `-r` | `--rooting` | Rooting file path |
| `-t` | `--threshold` | Bootstrap threshold |
| `-x` | `--modelCond` | Single model condition (occupancy) |
| `-y` | | Model reorder file |
| `-w` | | Clade reorder file |
| `-k` | `--missing` | Missing data flag (1=partial missing as complete) |
| `-g` | `--outgroup` | Outgroup name (relative frequency) |
| `-s` | `--style` | Color style set |

### 6.3 Command Examples

#### Species Tree Analysis

```bash
discoVista -m 0 -c examples/1KP/parameters/clade-defs.txt \
    -p examples/1KP/species/ -t 95 \
    -y examples/1KP/parameters/newModel.txt \
    -w examples/1KP/parameters/newOrders.txt \
    -o examples/1KP/results
```

#### Gene Tree Analysis

```bash
discoVista -m 1 -c examples/1KP/parameters/clade-defs.txt \
    -p examples/1KP/genetrees/filtered/ -t 75 \
    -y examples/1KP/parameters/newModel.txt \
    -w examples/1KP/parameters/newOrders.txt \
    -o examples/1KP/results
```

#### GC Content Analysis

```bash
discoVista -m 2 -p examples/1KP/GC/unfiltered/ \
    -o examples/1KP/results
```

#### Occupancy Analysis

```bash
discoVista -m 3 -a examples/1KP/parameters/annotation.txt \
    -p examples/1KP/occupancy/filtered/ \
    -o examples/1KP/results
```

#### Branch Statistics

```bash
discoVista -m 4 -p examples/1KP/branchAnalysis/ \
    -r examples/1KP/parameters/rooting.txt \
    -o examples/1KP/results
```

#### Relative Frequency Analysis

```bash
discoVista -m 5 \
    -a examples/1KP/parameters/annotation-1.txt \
    -p examples/1KP/relativeFreq/astral.trim50genes33taxa.no3rd.final-FNA2AA/ \
    -o examples/1KP/results/anot1 -g Base
```

### 6.4 Threshold Guide

- **Species tree analysis (mode 0)**: Typically 95 (bootstrap) or 0.95 (local posterior probability)
- **Gene tree analysis (mode 1)**: Typically 75
- Thresholds ≤ 1.0 are automatically multiplied by 100

---

## 7. GUI Usage

### 7.1 Launching

```bash
discoVista-gui
```

Or run `DiscoVista-Next.exe` directly.

### 7.2 Interface Layout

1. **Top Area**: Analysis mode selector + Theme selector
2. **Parameters Area** (scrollable): All input fields with browse buttons
3. **Action Buttons**: Load Example Data, Run Analysis, Clear
4. **Progress Bar**: Visible during analysis
5. **Log Output**: Shows analysis output
6. **Status Bar**: Current status

### 7.3 Theme Selection

All 26 qt-material themes are built-in (9 dark + 17 light). Switch via dropdown or menu bar (View → Theme).

### 7.4 Language Switching

- Menu bar → Language → Chinese/English

### 7.5 Loading Example Data

Click "Load Example Data" button to auto-fill all parameter paths for the 1KP species tree analysis example.

### 7.6 Running Analysis

1. Select analysis mode
2. Fill in required parameters (data path and output directory are required)
3. Fill in optional parameters based on mode:
   - Mode 0, 1: Clade definition file + threshold
   - Mode 3, 5: Annotation file
   - Mode 4: Rooting file
4. Click "Run Analysis"
5. Monitor progress and log
6. Results saved to output directory

---

## 8. Output Files

### 8.1 Species/Gene Tree Analysis (Mode 0, 1)

| File | Description |
|------|-------------|
| `clades.txt.res` | Clade analysis results (all branches) |
| `clades.hs.txt.res` | Clade analysis results (high support) |
| `*.block.pdf` | Classification heatmap |
| `*.block-shades.pdf` | Support value gradient heatmap |
| `Monophyletic_Bargraphs.pdf` | Gene tree bar charts (counts) |
| `Monophyletic_Bargraphs_Porportion.pdf` | Gene tree proportional bar charts |
| `Monophyletic_Bootstrap_Support_2.pdf` | Bootstrap support distribution histograms |

### 8.2 GC Content Analysis (Mode 2)

| File | Description |
|------|-------------|
| `gc-stat.csv` | GC statistics |
| `pTpP_GC_point.pdf` | GC content scatter plot |
| `pTpP_GC_boxplot.pdf` | GC content boxplot |

### 8.3 Occupancy Analysis (Mode 3)

| File | Description |
|------|-------------|
| `occupancy.csv` | Raw occupancy data |
| `occupancy-final.csv` | Species-level statistics |
| `occupancy-clades-final.csv` | Clade-level statistics |
| `occupancy.pdf` | Species occupancy line plot |
| `occupancy_clades.pdf` | Clade occupancy line plot |
| `occupancy_map.pdf` | Single model condition heatmap |

### 8.4 Branch Statistics (Mode 4)

| File | Description |
|------|-------------|
| `branchStats.csv` | Branch statistics |
| `branchSupport.csv` | Branch support values |
| `histogram_MLBS_distribution.pdf` | MLBS distribution histogram |
| `average_taxa_distance_vs_MLBS.pdf` | Average distance vs support |
| `maximum_taxa_distance_vs_MLBS.pdf` | Maximum distance vs support |

### 8.5 Relative Frequency Analysis (Mode 5)

| File | Description |
|------|-------------|
| `freqQuadCorrected.csv` | Corrected quartet frequencies |
| `relativeFreq.pdf` | Relative frequency plots |
| `tree.pdf` | Species tree visualization |

---

## 9. Example Data

The 1KP plant dataset is included in `examples/1KP/` directory. Use the "Load Example Data" button in the GUI for quick setup.

---

## 10. Theme List

All 26 qt-material color themes are built-in:

**Dark Themes (9):** Amber, Blue, Cyan, Lightgreen, Pink, Purple, Red, Teal (default), Yellow

**Light Themes (17):** Amber, Blue, Blue 500, Cyan, Cyan 500, Lightgreen, Lightgreen 500, Orange, Pink, Pink 500, Purple, Purple 500, Red, Red 500, Teal, Teal 500, Yellow

---

## 11. Citation

> Sayyari, E., Whitfield, J. B., & Mirarab, S. (2018). DiscoVista: Interpretable Visualizations of Gene Tree Discordance. *Molecular Phylogenetics and Evolution*, 122, 110-115.
