# StereonetForge

**Author:** Dr. Aram Fathian  
**Affiliation:** Department of Earth, Energy, and Environment; Water, Sediment, Hazards, and Earth-surface Dynamics (waterSHED) Lab; University of Calgary  
**License:** MIT

StereonetForge is a dependency-light **stereonet** plotter for planar geology data (e.g., Dip / Dip Direction).  
It works with **one** or **many groups** (or no group column), computes **mean planes**, **KDE pole-density rings**, and optional **intersection lines** between mean planes.

## How to cite
```
Fathian, A. (2025). StereonetForge (v0.2.1) [Software]. Zenodo. https://doi.org/10.5281/zenodo.17140123
```

## Install

**Option A — from GitHub (recommended until on PyPI)**
```bash
python -m pip install "git+https://github.com/aramfathian/StereonetForge.git@main"
```

**Option B — from a numbered tag**
```bash
python -m pip install "git+https://github.com/aramfathian/StereonetForge.git@v0.2.1"
# If you see "did not match any file(s) known to git", use the exact tag listed on the Releases page.
```

**Option C — from the local folder**
```bash
python -m pip install .
```

> Once published to PyPI, users can do: `pip install stereonet-forge`

## Command Line
```bash
# Single group (no group column)
stereonet-plot examples_general/example_one_group.csv --out-prefix ex1

# With group column 'Set'
stereonet-plot examples_general/example_two_groups.csv --group-col Set --out-prefix ex2

# Only Strike + Dip (derive Dip Direction)
stereonet-plot examples_general/example_three_groups_strike.csv --group-col Group --dip-col Dip --out-prefix ex3

# Combined 'Dip/DipDir' column called Dip_DD
stereonet-plot examples_general/example_combined_column.csv --group-col Domain --out-prefix ex4
```

### Options
- `--dip-col`, `--dipdir-col`, `--group-col` (auto-detects if omitted; can parse combined "Dip/DipDir")
- `--intersections none|auto|all|A|B,B|C`
- `--cmap tab10` (colormap per group), `--kde-bandwidth 0.09`
- `--figsize 10.5,10.5`, `--dpi 170`

## Library
```python
from stereonet_forge import plot_stereonet_from_csv, Style
fig, ax = plot_stereonet_from_csv("my.csv", group_col="Face", out_prefix="myplot")
```

## Development
- See **CONTRIBUTING.md** for guidelines.
- Typical build & publish:
```bash
python -m pip install --upgrade build twine
python -m build
twine check dist/*
twine upload dist/*
```
