# Developer Guide

## 1. Project Architecture

```
DiscoVista-Next-项目代码/
├── discovista_next/          # Main package
│   ├── __init__.py           # Package init, version, mode constants
│   ├── core/                 # Core analysis modules
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration & options (replaces reader.py)
│   │   ├── analyzer.py       # Analysis controller (replaces analyze.py)
│   │   ├── tree_tools.py     # Tree operations (replaces tools.py)
│   │   ├── find_clades.py    # Clade monophyly detection (replaces find_clades2.py)
│   │   ├── gc_stats.py       # GC content statistics (replaces gc_stats.py)
│   │   ├── occupancy.py      # Occupancy analysis (replaces occupancy.R data prep)
│   │   └── relative_freq.py  # Relative frequency (replaces map_names.py etc.)
│   ├── viz/                  # Visualization modules (replaces all R ggplot2)
│   │   ├── __init__.py
│   │   ├── depict_clades.py  # Clade heatmaps/bar charts (replaces main_depict_clades.R)
│   │   ├── gc_plot.py        # GC visualization (replaces plot.gc.R)
│   │   ├── occupancy_plot.py # Occupancy visualization (replaces occupancy.R plots)
│   │   ├── branch_stat_plot.py # Branch stat visualization (replaces branchStat.R)
│   │   ├── tree_plot.py      # Tree drawing (replaces plotTree.R)
│   │   └── relative_freq_plot.py # Relative frequency visualization
│   ├── cli/                  # Command-line interface
│   │   ├── __init__.py
│   │   └── main.py           # CLI entry point (replaces discoVista.py)
│   └── gui/                  # Graphical user interface
│       ├── __init__.py
│       ├── i18n.py           # Internationalization (Chinese/English)
│       └── main.py           # GUI main window
├── docs/                     # Documentation
│   ├── zh/                   # Chinese documentation
│   └── en/                   # English documentation
├── examples/                 # Example data
├── setup.py                  # Installation configuration
├── requirements.txt          # Dependency list
└── README.md                 # Project README
```

## 2. Module Mapping

### 2.1 R → Python Mapping

| Original R Script | Python Replacement | Description |
|-------------------|-------------------|-------------|
| `reader.R` | `core/config.py` | Options parsing |
| `depict_clades.R` | `viz/depict_clades.py` | Clade plotting entry |
| `main_depict_clades.R` | `viz/depict_clades.py` | Core plotting functions |
| `plot.gc.R` | `viz/gc_plot.py` | GC content plotting |
| `occupancy.R` | `core/occupancy.py` + `viz/occupancy_plot.py` | Occupancy analysis + plots |
| `branchStat.R` | `viz/branch_stat_plot.py` | Branch stat plotting |
| `plotTree.R` | `viz/tree_plot.py` | Tree drawing |

### 2.2 Python 2 → Python 3 Mapping

| Original Python 2 Module | Python 3 Replacement | Description |
|-------------------------|---------------------|-------------|
| `discoVista.py` | `cli/main.py` | Main entry |
| `analyze.py` | `core/analyzer.py` | Analysis controller |
| `reader.py` | `core/config.py` | Options handling |
| `tools.py` | `core/tree_tools.py` | Tree operations |
| `find_clades2.py` | `core/find_clades.py` | Clade analysis |
| `gc_stats.py` | `core/gc_stats.py` | GC statistics |
| `map_names.py` | `core/relative_freq.py` | Relative frequency |
| `generate_clade-defs.py` | (retained, updated to Python 3) | Clade definition generation |

### 2.3 Shell Script Replacements

| Original Shell Script | Python Replacement | Description |
|----------------------|-------------------|-------------|
| `pos-for-hyp.sh` | `core/relative_freq.py` `run()` | Relative frequency workflow |
| `branchLengthCompare.sh` | (integrated into `tree_tools.py`) | Branch length comparison |
| `maxOrAvgDistances.sh` | (integrated into `tree_tools.py`) | Distance calculation |

## 3. Core Design

### 3.1 Configuration Management

The `Options` dataclass encapsulates all runtime parameters, built via the `from_args()` factory method.

```python
from discovista_next.core import Options

opt = Options.from_args(["-m", "0", "-p", "data/", "-c", "clades.txt",
                          "-t", "95", "-o", "results/"])
```

### 3.2 Analysis Flow

The `Analyzer` class dispatches to the appropriate analysis method based on the `mode` field:

```python
from discovista_next.core import Analyzer

analyzer = Analyzer(opt)
analyzer.analyze()  # Automatically selects the correct analysis mode
```

### 3.3 Visualization Architecture

All visualizations use matplotlib's `Agg` backend (non-interactive), ensuring they work in headless server environments. Each visualization class handles one chart type.

### 3.4 GUI Architecture

- **i18n.py**: Centralized management of all UI text translations
- **main.py**: Main window with menu bar, parameter input area, log output, and background worker thread
- **AnalysisWorker**: Inherits from `QObject`, runs analysis in a `QThread` to avoid blocking the UI

## 4. Extension Development

### 4.1 Adding a New Analysis Mode

1. Add a mode constant in `__init__.py`
2. Create a new analysis module in `core/`
3. Add dispatch logic in `core/analyzer.py`
4. Create corresponding visualization in `viz/`
5. Update the GUI mode dropdown

### 4.2 Adding a New Visualization

```python
from discovista_next.viz import DepictClades

# Custom visualization
class MyPlot:
    def __init__(self, out_dir):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    def plot(self, data):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        # ... plotting code ...
        fig.savefig(os.path.join(self.out_dir, "my_plot.pdf"))
        plt.close(fig)
```

### 4.3 Adding a New Interface Language

Add new language mappings in the `TRANSLATIONS` dictionary in `gui/i18n.py`, and add an option in the language menu.

## 5. Testing

```bash
# Run basic tests
python -m discovista_next.cli.main --help

# Test with example data
discoVista -m 0 -c examples/clade-defs.txt -p examples/species/ \
    -t 95 -o examples/results/
```

## 6. Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request
