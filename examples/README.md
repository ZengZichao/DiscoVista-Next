# Example Data

This directory holds the **1KP plant dataset**, used to try out the analysis modes of
DiscoVista-Next.

## Included in this repository

```
examples/1KP/
├── README              # Original DiscoVista data layout notes
└── parameters/         # Parameter files (included)
    ├── annotation.txt      # Species → clade annotation
    ├── annotation-1.txt    # Alternative annotation split
    ├── clade-defs.txt      # Clade (split) definitions
    ├── rooting.txt         # Outgroup and rooting definitions
    ├── newModel.txt        # Model condition reordering
    ├── newOrders.txt       # Clade reordering
    └── ...
```

## Fetched separately

The large data files — gene trees, sequence data, GC content, occupancy, branch
statistics, relative frequency (about 400 MB unpacked, 8600+ files) — are not bundled.
From the project root, run:

```bash
python examples/fetch_data.py
```

The script downloads each data package (`tar.gz`) from the original
[DiscoVista](https://github.com/esayyari/DiscoVista) repository and extracts it into
`examples/1KP/`:

| Package | Contents |
|---------|----------|
| `genetrees.tar.gz` | Gene trees (several support-filtered versions) |
| `species.tar.gz` | Species trees |
| `GC.tar.gz` | GC content analysis data |
| `occupancy.tar.gz` | Occupancy analysis data |
| `branchAnalysis.tar.gz` | Branch support vs branch length data |
| `relativeFreq.tar.gz` | Relative frequency analysis data |

## What the directory looks like once the data is in place

```
examples/1KP/
├── parameters/
├── genetrees/
├── species/
├── GC/
├── occupancy/
├── branchAnalysis/
└── relativeFreq/
```

At that point, click **Load Example Data** in the GUI or run the example commands from
the README to reproduce the results of each analysis mode.

> The downloaded data does not need to be committed — `.gitignore` excludes everything
> under `examples/1KP/` except `parameters/` and `README`.

## Using your own data

The directory layout of the example data is the input convention of DiscoVista-Next. See
the [User Guide](../docs/en/user_guide.md) (English) or
[使用手册](../docs/zh/user_guide.md) (Chinese) for details.
