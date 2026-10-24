# Installation Guide

## System Requirements

- Python 3.8 or higher
- Operating System: Windows / macOS / Linux
- Disk space: about 500 MB for the dependencies, plus about 400 MB if you also want the optional 1KP example dataset

## Installation Methods

### Method 1: Install from Source (Recommended for Developers)

#### 1. Install Python 3

Ensure Python 3.8+ is installed:

```bash
python --version
```

#### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

#### 3. Install DiscoVista-Next

```bash
# Navigate to project directory
cd DiscoVista-Next-项目代码

# Install dependencies and package
pip install -e .
```

Or install dependencies manually:

```bash
pip install -r requirements.txt
```

#### 4. Verify Installation

```bash
# CLI tool
discoVista --help

# GUI tool
discoVista-gui
```

### Method 2: Use Standalone EXE (Recommended for End Users)

1. Obtain `DiscoVista-Next.exe`
2. Double-click to run — no Python installation needed
3. The exe includes all dependencies (example data is not bundled)

### Method 3: Build Standalone EXE

See the "Building EXE" section below.

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| dendropy | >= 4.5.0 | Phylogenetic tree reading and manipulation |
| matplotlib | >= 3.5.0 | Data visualization |
| pandas | >= 1.3.0 | Data processing |
| numpy | >= 1.20.0 | Numerical computation |
| seaborn | >= 0.11.0 | Statistical plotting |
| PySide6 | >= 6.4.0 | GUI framework |
| qt-material | >= 2.17 | Material Design themes (26 built-in themes) |
| pyinstaller | >= 5.0 | Building standalone exe (optional) |

## Building Standalone EXE

### Prerequisites

```bash
pip install pyinstaller
pip install -e .
```

### Method 1: Using Build Script

```bash
python build_exe.py
```

### Method 2: Using Spec File

```bash
pyinstaller DiscoVista-Next.spec
```

### Build Output

The standalone exe will be at `dist/DiscoVista-Next.exe`.

### Notes

- The exe includes all dependencies (~200-400MB)
- First launch may be slow (extracting temporary files)
- Build process may take 5-10 minutes

## Common Installation Issues

### Issue: PySide6 Installation Fails

PySide6 is a large package. Try:

```bash
pip install PySide6 --no-cache-dir
```

### Issue: matplotlib Backend Error

The code uses the `Agg` backend by default (set in code).

### Issue: CLI Tool Not Found on Windows

Ensure Python Scripts directory is in PATH. Or use:

```bash
python -m discovista_next.cli.main [options]
```

### Issue: qt-material Themes Not Showing

```bash
pip install qt-material --upgrade
```

### Issue: ModuleNotFoundError During EXE Build

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
pip install pyinstaller
```
