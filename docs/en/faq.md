# Frequently Asked Questions (FAQ)

## 1. What is the difference between DiscoVista-Next and the original DiscoVista?

DiscoVista-Next is a complete Python 3 rewrite of the original DiscoVista. Key differences:

- **No R dependency**: The original requires R and multiple R packages; this version is fully Python
- **Python 3**: The original uses Python 2; this version is fully Python 3
- **GUI**: The original has only CLI; this version adds a qt-material-based GUI with 26 themes
- **Internationalization**: This version supports Chinese/English switching
- **Standalone EXE**: This version can be built as a self-contained executable
- **Example data**: the 1KP parameter files ship with the repository; the large data files (~400 MB) are downloaded separately — see `examples/README.md`

## 2. Can I use the original DiscoVista data files?

Yes. DiscoVista-Next maintains full compatibility with the original data directory structure and input file formats.

## 3. What does relative frequency analysis (mode 5) require?

Mode 5 requires running ASTRAL (DiscoVista branch) first to generate the `freqQuad.csv` file. Place it in your data directory.

## 4. How do I choose the correct bootstrap threshold?

- Species tree analysis: typically 95 (bootstrap) or 0.95 (local posterior probability)
- Gene tree analysis: typically 75

## 5. The GUI shows a black or white screen on startup?

Try updating qt-material:

```bash
pip install --upgrade qt-material
```

## 6. How to run without a display (headless server)?

The visualization modules use matplotlib's `Agg` backend, which works without a display. Use CLI mode:

```bash
discoVista -m 0 -c clade-defs.txt -p data/ -t 95 -o results/
```

## 7. Output directory has only CSV files, no PDF charts?

Check:
1. matplotlib and seaborn are properly installed
2. Log shows no plotting-related errors
3. Output directory has write permissions

## 8. How many themes are available?

26 built-in qt-material themes (9 dark + 17 light). Switch via dropdown or menu bar.

## 9. The EXE file is very large. Can I reduce the size?

The exe bundles all dependencies, but not the example data. To use the "Load Example Data" feature, place the 1KP dataset under an `examples/` directory next to the exe.

## 10. The EXE takes a long time to start on first run?

This is normal. PyInstaller extracts temporary files on first run. Subsequent launches are faster.

## 11. How to report bugs?

Please create an Issue in the project repository with:
- Operating system and Python version
- Complete command line parameters
- Error log output
