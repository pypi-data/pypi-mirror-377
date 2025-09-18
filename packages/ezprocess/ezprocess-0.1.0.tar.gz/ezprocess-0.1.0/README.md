# ezprocess

**Preprocess, tile, load, and analyze rasters for flood‑depth prediction and related geospatial ML(Machine Learning)/Deep Learning (DL) tasks.**

> A lightweight utility library that prepares geospatial rasters for machine/deep‑learning: LiDAR gridding (DEM/DSM/nDSM), normalization and transformation, consistent tiling across aligned layers, dataset sampling and visualization, ML/DL‑ready loading & batching with optional geometric augmentation, and exploratory analysis (stats, correlation, VIF, redundancy, distributions, and feature importance).

---

## Features

- **LiDAR → DEM/DSM/nDSM**: one‑function gridding from point cloud files (LAS/LAZ).
- **Transform(where appropriate) & Normalization**: global min–max, RGB normalization, log1p, cube‑root.
- **Consistent tiling**: window tiles across *aligned* rasters using a reference layer.
- **Dataset curation**: filter tiles by target sparsity, random sampling, quick visual QA.
- **ML/DL Input/Output**: load aligned tiles to `(N,H,W,C)` arrays, split train/val/test, and batch with the option of geometry‑only augmentation.
- **Data analysis**: tidy descriptive stats, correlations, VIF, redundancy pairs, distributions, and feature importance via RF/XGBoost/SHAP.

---

## Installation

```bash
pip install ezprocess
```

> **Note on `rasterio`/GDAL**: Use a recent Python (≥3.9) and prefer wheels (e.g., via pip/conda‑forge). On Windows, installing `rasterio` from wheels avoids most GDAL issues.

---

## Quickstart

```python
from ezprocess import PreProcess, Tiles, Implement, Xplore
```

### 1) LiDAR to DEM/DSM/nDSM

```python
out = PreProcess.SimpleLidar(
    input_folder="/path/to/laz_las/",
    output_folder="/path/to/out/",
    epsg=32119,                # example EPSG
    products=("DEM","DSM","nDSM"),
    cellsize=1.0,
)
# out => {"DEM": "...DEM.tif", "DSM": "...DSM.tif", "nDSM": "...nDSM.tif"}
```

### 2) Transform(where appropriate) & Normalize rasters

```python
# Get global range from a folder of rasters (e.g., depth tiles)
mx, mn = PreProcess.GlobRange("/path/to/depth/")

# Min–Max normalize into [0,1]
PreProcess.MinMaxNorm("/path/to/depth/", "/path/to/depth_norm/", mn, mx)

# Optional transforms
PreProcess.LogTransform("/path/in/", "/path/out/")
PreProcess.CubeRootTransform("/path/in/", "/path/out/")
# RGB normalization write (dtype→float32)
PreProcess.NormRGB("/path/rgb_in/", "/path/rgb_out/")
```

### 3) Create consistent tiles across layers

```python
input_folders = {
    "imagery": "/data/img/",
    "dem":     "/data/dem/",
    "extent":  "/data/extent/",
    "depth":   "/data/depth/",   # reference target
}
output_folders = {
    "out_imagery": "/tiles/img/",
    "out_dem":     "/tiles/dem/",
    "out_extent":  "/tiles/extent/",
    "out_depth":   "/tiles/depth/",
}

# Tiling (256×256, no overlap) using the 'depth' layer as the window reference
stats = Tiles.CreateTiles(
    input_folders, output_folders,
    tile_size=(256,256), overlap=0, reference_key="depth"
)
```

#### Filter & sample tiles

```python
# Keep tiles whose target has <50% zeros (adjust threshold as needed)
Tiles.FilterTiles(
    reference_folder=output_folders["out_depth"],
    input_folders={k: v for k, v in output_folders.items() if k != "out_depth"},
    output_folders={k: v.replace("/tiles/", "/tiles_filt/") for k, v in output_folders.items()},
    reference_key="depth", threshold=0.5,
)

# Randomly sample a fixed number from the filtered pool for experiments
Tiles.SampleTiles(
    input_folders={
        "imagery": "/tiles_filt/img/",
        "dem":     "/tiles_filt/dem/",
        "extent":  "/tiles_filt/extent/",
        "depth":   "/tiles_filt/depth/",
    },
    output_folders={
        "out_imagery": "/tiles_samp/img/",
        "out_dem":     "/tiles_samp/dem/",
        "out_extent":  "/tiles_samp/extent/",
        "out_depth":   "/tiles_samp/depth/",
    },
    ref_key="depth", sample_size=500,
)

# Visual spot‑check matching tiles across categories
Tiles.VisualizeTiles(
    {
      "imagery": "/tiles_samp/img/",
      "dem":     "/tiles_samp/dem/",
      "extent":  "/tiles_samp/extent/",
      "depth":   "/tiles_samp/depth/",
    },
    num_samples=2, figsize_per_tile=(4,4)
)
```

### 4) ML/DL‑ready arrays + batching with augmentation

```python
# Align on common filenames and stack features into channels
X, y = Implement.LoadTiles(
    feature_folders={
        "DEM":    "/tiles_samp/dem/",
        "EXTENT": "/tiles_samp/extent/",
        "IMG":    "/tiles_samp/img/",
    },
    target_folder="/tiles_samp/depth/",
    size=(256,256)
)

# Train/Val/Test split
Xtr, ytr, Xva, yva, Xte, yte = Implement.ShuffleSplit(X, y, 0.7, 0.15, 0.15, seed=42)

# Keras‑compatible generator with geometry‑only augmentation
pipe = Implement.SimplePipeline(
    Xtr, ytr,
    batch_size=16,
    shuffle=True,
    augment=True,
    aug_ops=("hflip","vflip","rot90","rot180","rot270","transpose"),
    aug_prob=0.5,
)
# model.fit(pipe, validation_data=(Xva, yva), epochs=...)  # example usage
```

### 5) Exploratory analysis (EDA)

```python
folders = {
  "DEM":    "/rasters/dem/",
  "EXTENT": "/rasters/extent/",
  "DEPTH":  "/rasters/depth/",   # set your target key here
}
x = Xplore(folders, y="DEPTH")

# Descriptive stats (as tidy DataFrame)
desc = x.DescStats(round_to=3)

# Correlations + heatmap (Pearson or Spearman)
corr, target_corr = x.CorrAnalysis(method="pearson", save_csv=None)

# Low‑variance features
low_var = x.VarAnalysis(threshold=1e-2)

# Multicollinearity (VIF)
vif = x.VIF(round_to=3)

# Redundant pairs above 0.95 abs‑corr
pairs = x.FeatRedundancy(threshold=0.95, method="pearson")

# Target distribution summary + plot
summ = x.yDist(bins=40, kde=True)

# Predictors distributions
x.XDist(kde=True, max_cols=4)

# Feature importance (RF/XGB/SHAP)
imp = x.FeatImportance(method="rf", plot=True)
```

---

## API Overview

### `PreProcess`
- `SimpleLidar(input_folder, output_folder, epsg, products=("DEM","DSM","nDSM"), cellsize=1.0)`
- `GlobRange(folder_path)` → `(global_max, global_min)`
- `MinMaxNorm(input_folder, output_folder, min_value, max_value)`
- `NormRGB(input_folder, output_folder)`
- `LogTransform(input_folder, output_folder)`
- `CubeRootTransform(input_folder, output_folder)`

### `Tiles`
- `CreateTiles(input_folders, output_folders, tile_size=(256,256), overlap=0, reference_key='depth')`
- `FilterTiles(reference_folder, input_folders, output_folders, reference_key='depth', threshold=0.5)`
- `SampleTiles(input_folders, output_folders, ref_key='depth', sample_size=500)`
- `VisualizeTiles(folder_paths, num_samples=1, figsize_per_tile=(4,4), cmap='viridis')`

### `Implement`
- `LoadTiles(feature_folders, target_folder, size=(256,256), extensions=(".tif",".tiff"), dtype=np.float32)`
- `ShuffleSplit(X, y, train_size=0.6, val_size=0.2, test_size=0.2, seed=42, shuffle=True, verbose=True)`
- `SimplePipeline(X, y, batch_size=32, shuffle=True, augment=False, aug_ops=(...), aug_prob=0.5, seed=None)`

### `Xplore`
- `DescStats(percentiles=(0.25,0.5,0.75), round_to=4, save_csv=None)`
- `CorrAnalysis(method='pearson', save_csv=None, figsize=(10,8))`
- `VarAnalysis(threshold=0.01)`
- `VIF(target_col=None, round_to=3, save_csv=None)`
- `FeatRedundancy(threshold=0.95, method='pearson', exclude_target=True, round_to=3)`
- `BoxPlot(columns=None, exclude_target=False, whisker_k=1.5, round_to=3)`
- `yDist(target_col=None, bins=30, kde=True, dropna=True, log_x=False, figsize=(8,4), round_to=3)`
- `XDist(columns=None, exclude_target=True, bins=30, kde=True, max_cols=4, per_plot_size=(4,3))`
- `FeatImportance(method='rf'|'xgb'|'shap', target_col=None, sample_size=10000, plot=True, shap_summary=False, model_params=None, return_model=False, random_state=42)`

---

## Tips & Conventions

- All rasters that you intend to tile together should be **aligned** (same pixel grid, extent, and CRS) and use **identical filenames** across folders.
- `Tiles.CreateTiles` uses the `reference_key` layer to define windows; every other layer is sliced by these same windows.
- Prefer float32 rasters for ML/DL; normalize targets (e.g., depth) to [0,1] if your model expects it.
- For heavy datasets, use on‑disk generators and small `batch_size` to manage memory.

---

## Contributing

PRs and issues are welcome. Please open an issue for bugs or feature requests. Add minimal examples and expected behavior.

---

## License

MIT — see `LICENSE`.

---

## Citation

If you use **ezprocess** in academic work, please cite this repository and include library version (`ezprocess==0.1.0`).
