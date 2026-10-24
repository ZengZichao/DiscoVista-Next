# DiscoVista-Next

**Phylogenetic Discordance Visualization & Analysis Tool** — Complete Python 3 Rewrite

## Overview

DiscoVista-Next is a complete Python 3 rewrite of the original [DiscoVista](https://github.com/esayyari/DiscoVista) (Discordance Visualization Tool), originally written by Erfan Sayyari and Siavash Mirarab using Python 2 + R. This version replaces all R dependencies (ggplot2, reshape2, plyr, ape, optparse, etc.) with Python 3 equivalents and adds a qt-material-based GUI.

## Key Features

- **Pure Python 3**: No R language or R package dependencies
- **6 Analysis Modes**: Species tree discordance, gene tree discordance, GC content, occupancy, branch statistics, relative frequency
- **Complete Visualization**: Uses matplotlib + seaborn to replace ggplot2
- **GUI**: Modern qt-material-based interface with Chinese/English switching and light/dark theme
- **CLI**: Backward-compatible command-line interface

## Quick Start

```bash
# Install
pip install -e .

# Command-line
discoVista -m 0 -c clade-defs.txt -p data/ -t 95 -o results/

# Launch GUI
discoVista-gui
```

## Documentation

| Document | Description |
|----------|-------------|
| [Installation](en/installation.md) | Detailed installation steps |
| [User Guide](en/user_guide.md) | Complete usage tutorial |
| [Developer Guide](en/developer_guide.md) | Architecture and development guide |
| [API Reference](en/api_reference.md) | Full API documentation |
| [FAQ](en/faq.md) | Frequently asked questions |

| 文档 | 说明 |
|------|------|
| [安装指南](zh/installation.md) | 详细安装步骤 |
| [使用手册](zh/user_guide.md) | 完整使用教程 |
| [开发者文档](zh/developer_guide.md) | 架构设计与开发指南 |
| [API 参考](zh/api_reference.md) | 完整 API 文档 |
| [FAQ](zh/faq.md) | 常见问题解答 |

## Citation

If you use DiscoVista-Next in your research, please cite the original paper:

> Sayyari, E., Whitfield, J. B., & Mirarab, S. (2018). DiscoVista: Interpretable Visualizations of Gene Tree Discordance. *Molecular Phylogenetics and Evolution*, 122, 110-115.

## License

GPL-3.0
