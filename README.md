# DiscoVista-Next

**Phylogenetic discordance visualization and analysis** — a complete Python 3 rewrite

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)]()

**English** | [简体中文](README.zh-CN.md)

## Overview

DiscoVista-Next is a complete Python 3 rewrite of the original
[DiscoVista](https://github.com/esayyari/DiscoVista) (Discordance Visualization Tool),
written by Erfan Sayyari and Siavash Mirarab on a mixed Python 2 + R stack. This version
reimplements every R dependency (ggplot2, reshape2, plyr, ape, optparse, …) in Python 3 and
adds a graphical interface built on qt-material.

## Key Features

- **Pure Python 3** — no R installation or R packages required
- **Six analysis modes** — species tree discordance, gene tree discordance, GC content,
  occupancy, branch statistics, relative frequency
- **Complete visualization** — matplotlib + seaborn replace ggplot2
- **Graphical interface** — modern qt-material GUI with 26 built-in color themes
- **Bilingual UI** — switch between English and Chinese at runtime
- **Command-line tool** — CLI compatible with the original DiscoVista argument format
- **Standalone executable** — build a self-contained exe that runs without a Python install
- **Example data** — 1KP plant dataset parameter files and a fetch script ship with the repo

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ZengZichao/DiscoVista-Next.git
cd DiscoVista-Next

# Install dependencies
pip install -r requirements.txt

# Install the package (development mode)
pip install -e .
```

### Command line

```bash
# Species tree discordance
discoVista -m 0 -c examples/1KP/parameters/clade-defs.txt \
    -p examples/1KP/species/ -t 95 -o results/

# Gene tree discordance
discoVista -m 1 -c examples/1KP/parameters/clade-defs.txt \
    -p examples/1KP/genetrees/filtered/ -t 95 -o results/

# GC content
discoVista -m 2 -p examples/1KP/GC/unfiltered/ -o results/

# Occupancy
discoVista -m 3 -p examples/1KP/occupancy/filtered/ \
    -a examples/1KP/parameters/annotation.txt -o results/

# Branch support vs branch length
discoVista -m 4 -p examples/1KP/branchAnalysis/ \
    -r examples/1KP/parameters/rooting.txt \
    -a examples/1KP/parameters/annotation.txt -o results/

# Relative frequency
discoVista -m 5 -p examples/1KP/relativeFreq/astral.trim50genes33taxa.no3rd.final-FNA2AA/ \
    -a examples/1KP/parameters/annotation.txt -o results/
```

### Launch the GUI

```bash
discoVista-gui
# or
python -m discovista_next.gui.main
```

### Use the standalone executable

Run `DiscoVista-Next.exe` directly — no Python installation needed.

1. Double-click `DiscoVista-Next.exe`
2. Click **Load Example Data** to fill in all input paths
3. Choose an analysis mode and adjust the parameters
4. Click **Run Analysis**
5. The generated figures appear in the **Plots** panel on the right

### Build the executable

```bash
python build_exe.py
# or
pyinstaller DiscoVista-Next.spec
```

The build output goes to `dist/DiscoVista-Next/`.

## Feature Coverage

DiscoVista-Next covers the full feature set of the original DiscoVista:

| Feature | Original | DiscoVista-Next |
|---------|----------|-----------------|
| Species tree discordance | ✅ | ✅ (mode 0) |
| Gene tree discordance | ✅ | ✅ (mode 1) |
| GC content analysis | ✅ | ✅ (mode 2) |
| Occupancy analysis | ✅ | ✅ (mode 3) |
| Branch support vs branch length | ✅ | ✅ (mode 4) |
| Relative frequency analysis | ✅ | ✅ (mode 5) |
| Clade definition file | ✅ | ✅ |
| Annotation file | ✅ | ✅ |
| Rooting file | ✅ | ✅ |
| Model condition reordering | ✅ | ✅ |
| Clade reordering | ✅ | ✅ |
| Missing data handling | ✅ | ✅ |
| Graphical interface | ❌ | ✅ (26 themes) |
| English/Chinese switching | ❌ | ✅ |
| Standalone exe | ❌ | ✅ |
| Example data | ✅ (manual download) | ✅ (in repository) |

## Project Structure

```
DiscoVista-Next/
├── discovista_next/           # Main package
│   ├── __init__.py            # Package init, analysis mode constants
│   ├── cli/                   # Command-line interface
│   │   └── main.py
│   ├── core/                  # Core analysis logic
│   │   ├── analyzer.py        # Analysis controller
│   │   ├── config.py          # Configuration and option handling
│   │   ├── find_clades.py     # Clade monophyly detection
│   │   ├── gc_stats.py        # GC content statistics
│   │   ├── occupancy.py       # Occupancy analysis
│   │   ├── relative_freq.py   # Relative frequency analysis
│   │   └── tree_tools.py      # Tree manipulation utilities
│   ├── gui/                   # Graphical interface
│   │   ├── main.py            # Main window
│   │   ├── i18n.py            # Internationalization
│   │   └── runtime_hook.py    # PyInstaller runtime hook
│   ├── resources/             # Icons and other resources
│   └── viz/                   # Visualization modules
│       ├── depict_clades.py   # Clade visualization
│       ├── gc_plot.py         # GC content plots
│       ├── occupancy_plot.py  # Occupancy plots
│       ├── branch_stat_plot.py # Branch statistics plots
│       ├── tree_plot.py       # Phylogenetic tree plots
│       └── relative_freq_plot.py # Relative frequency plots
├── docs/                      # Documentation
│   ├── en/                    # English docs
│   └── zh/                    # Chinese docs
├── examples/1KP/              # Example data (parameter files + fetch instructions)
├── build_exe.py               # PyInstaller build script
├── DiscoVista-Next.spec       # PyInstaller spec file
├── requirements.txt           # Python dependencies
├── setup.py                   # Installation configuration
├── LICENSE                    # GPL-3.0 license
├── README.md                  # This file (English)
└── README.zh-CN.md            # Chinese README
```

## Built-in Themes

DiscoVista-Next ships all 26 qt-material color themes:

- **Dark (9)**: Amber, Blue, Cyan, Lightgreen, Pink, Purple, Red, Teal, Yellow
- **Light (17)**: Amber, Blue, Blue 500, Cyan, Cyan 500, Lightgreen, Lightgreen 500, Orange, Pink, Pink 500, Purple, Purple 500, Red, Red 500, Teal, Teal 500, Yellow

## Example Data

The `examples/1KP/` directory in this repository contains the parameter files of the
1KP plant dataset:

- `parameters/annotation.txt` — species-to-clade annotation
- `parameters/clade-defs.txt` — clade (split) definitions
- `parameters/rooting.txt` — outgroup and rooting definitions
- `parameters/newModel.txt`, `parameters/newOrders.txt` — model condition and ordering

The large data files — gene trees, sequence alignments, GC content, occupancy and so on
(about 400 MB unpacked) — are not bundled. Fetch them from the original DiscoVista
repository:

```bash
python examples/fetch_data.py
```

Once the data is in place, click **Load Example Data** in the GUI to fill in all paths
automatically. See [examples/README.md](examples/README.md) for details.

## Documentation

| Document | Description |
|----------|-------------|
| [Installation Guide](docs/en/installation.md) | Detailed installation steps |
| [User Guide](docs/en/user_guide.md) | Complete usage tutorial |
| [Developer Guide](docs/en/developer_guide.md) | Architecture and development |
| [API Reference](docs/en/api_reference.md) | Complete API documentation |
| [FAQ](docs/en/faq.md) | Frequently asked questions |
| [安装指南 (中文)](docs/zh/installation.md) | Detailed installation steps (Chinese) |
| [使用手册 (中文)](docs/zh/user_guide.md) | Complete usage tutorial (Chinese) |
| [开发者文档 (中文)](docs/zh/developer_guide.md) | Architecture and development (Chinese) |
| [API 参考 (中文)](docs/zh/api_reference.md) | Complete API documentation (Chinese) |
| [FAQ (中文)](docs/zh/faq.md) | Frequently asked questions (Chinese) |

## Development

### Set up an environment

```bash
git clone https://github.com/ZengZichao/DiscoVista-Next.git
cd DiscoVista-Next
pip install -r requirements.txt
pip install -e .
```

### Build the executable

```bash
python build_exe.py
```

## Citation

If you use DiscoVista-Next in your research, please cite the original paper:

> Sayyari, E., Whitfield, J. B., & Mirarab, S. (2018). DiscoVista: Interpretable
> Visualizations of Gene Tree Discordance. *Molecular Phylogenetics and Evolution*,
> 122, 110-115.

## License

[GPL-3.0](LICENSE)
