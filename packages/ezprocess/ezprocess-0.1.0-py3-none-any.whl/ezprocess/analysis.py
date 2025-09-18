
"""
Created on Fri Aug 22 11:00:33 2025

@authors: Jeffrey Blay and Gazali Agboola 
"""

# IMPORT LIBRARIES
import os
import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
import shap
from xgboost import XGBRegressor
importances_df = None
from statsmodels.stats.outliers_influence import variance_inflation_factor


# CLASS WITH FUNCTIONS FOR DATA ANALYSIS
class Xplore:
    
    # Functions to initialize with raster folder paths, validate target, and load rasters into DataFrame
    
    def __init__(self, raster_folders: dict, y='DEPTH'):
        """
        Initialize with a dictionary of folder paths:
        Example:
        {
            'flood': '/path/to/flood_rasters/',
            'terrain': '/path/to/dem_rasters/',
            ...
        }
        """
        self.raster_folders = raster_folders
        self.raster_data = {}
        self.df = None
        
        # Define target
        if y not in raster_folders:
            raise KeyError(f"Target key '{y}' not found in raster_folders. Got: {list(raster_folders.keys())}")
        self.target_key = y 
        self.target = raster_folders[y]
        if not os.path.isdir(self.target):
            raise FileNotFoundError(f"Target folder does not exist: {self.target}")
        
        self._load_and_flatten_rasters()
        
        
        
    @staticmethod # This allows it to call it as self._resize_or_pad() without passing self. 
    def _resize_or_pad(array, target_shape):
        current_shape = array.shape
        padded = np.zeros(target_shape, dtype=array.dtype)
        
        min_rows = min(current_shape[0], target_shape[0])
        min_cols = min(current_shape[1], target_shape[1])
        
        padded[:min_rows, :min_cols] = array[:min_rows, :min_cols]
        return padded   
    
    # Load and flatten rasters    
    def _load_and_flatten_rasters(self):

        area_data = {}
        
        #step 1: Gather reference sizes from the DEPTH folder
        reference_shapes = {}
        
        for file in os.listdir(self.target):
            if file.endswith(".tif"):
                area_name = os.path.splitext(file)[0]
                with rasterio.open(os.path.join(self.target,file)) as src:
                    reference_shapes[area_name] = src.read(1).shape
                    
            
        # Step 2: Load all rasters, resize or pad to match reference shape
        for dtype, folder in self.raster_folders.items():
            for fname in os.listdir(folder):
                if fname.endswith('.tif'):
                    area_name = os.path.splitext(fname)[0]
                    file_path = os.path.join(folder, fname)
    
                    with rasterio.open(file_path) as src:
                        arr = src.read(1)
                    
                    target_shape = reference_shapes.get(area_name)
                    if target_shape is None:
                        continue # skip if no reference
                        
                    # Resize or pad raster to match the reference depth shape
                    arr = self._resize_or_pad(arr, target_shape)
                    
                    if area_name not in area_data:
                        area_data[area_name] = {}
                    area_data[area_name][dtype] = arr
                    
        # Step 3: Flatten into DataFrame
        records = []
        for area_name, data_dict in area_data.items():
            if len(data_dict) == len(self.raster_folders):
                stacked = np.stack([data_dict[key] for key in sorted(data_dict)], axis=-1)
                flat = stacked.reshape(-1, stacked.shape[-1])
                records.append(flat)
            
        all_data = np.vstack(records)
        df = pd.DataFrame(all_data, columns=sorted(self.raster_folders))
        
        # Remove rows with any 0 values (treated as NaNs)
        self.df = df[(df != 0).all(axis=1)]
        
    # Basic Descriptive Statistics    
    def DescStats(self, percentiles=(0.25, 0.5, 0.75), round_to=4, save_csv=None):
        """
        Return descriptive statistics as a tidy DataFrame.
        Optional:
          - percentiles: tuple of percentiles to include (default: quartiles)
          - round_to: decimals to round output
          
          - save_csv: path to save the table as CSV
          sampleuse: x.DescStats(round_to=3, save_csv="path")
        """
        if self.df is None or self.df.empty:
            raise ValueError("No data available. Make sure rasters loaded into self.df.")
    
        num_df = self.df.select_dtypes(include=[np.number])
    
        # Core describe() and extras
        desc = num_df.describe(percentiles=percentiles).T
        desc["missing"]   = num_df.isna().sum()
        desc["valid_n"]   = num_df.notna().sum()
        # pandas 2.x supports numeric_only; older versions ignore it—safe either way
        desc["skew"]      = num_df.skew(numeric_only=True)
        desc["kurtosis"]  = num_df.kurtosis(numeric_only=True)
        
        # Convenience metric- compute interquartile range if .75 provided.
        if "75%" in desc.columns and "25%" in desc.columns:
            desc["iqr"] = desc["75%"] - desc["25%"]
    
        # Nice column order (only keep those that exist)
        order = ["count","valid_n","missing","mean","std","min","25%","50%","75%","iqr","max","skew","kurtosis"]
        desc = desc[[c for c in order if c in desc.columns]].round(round_to)
        
        # Save result to csv if requested
        if save_csv:
            desc.to_csv(save_csv)
    
        return desc
    
    # Correlation Analysis
    def CorrAnalysis(self, method='pearson', save_csv=None, figsize=(10, 8)):
        """
        Compute and plot a correlation matrix (pearson or spearman),
        print a markdown table of correlations with the target column,
        and optionally save the full matrix to CSV.
    
        Parameters
        ----------
        method : {'pearson','spearman'}
        save_csv : str or None - output savepath
            If provided, path to save the full correlation matrix as CSV.
        figsize : tuple
            Size of the heatmap figure.
        
        sample use-corr_df, tgt_corr = x.correlation_analysis(method='spearman', save_csv='corr_spearman.csv')
        """
        if self.df is None or self.df.empty:
            raise ValueError("No data available. Make sure rasters loaded into self.df.")
    
        method = str(method).lower()
        if method not in ('pearson', 'spearman'):
            method = 'pearson'  # fallback
    
        # Numeric-only correlation
        num_df = self.df.select_dtypes(include=[np.number])
        corr = num_df.corr(method=method)
    
        # Plot heatmap 
        plt.figure(figsize=figsize)
        sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', square=True)
        plt.title(f'{method.title()} Correlation Matrix')
        plt.tight_layout()
        plt.show()
    
        # Find target column name from self.target (which stores the folder path) 
        target_col = next((k for k, v in self.raster_folders.items() if v == self.target), None)
    
        # Print markdown table of target correlations (sorted) 
        target_corr = None
        if target_col and target_col in corr.columns:
            target_corr = corr[target_col].sort_values(ascending=False)
            try:
                print(target_corr.to_markdown())
            except Exception:
                print(target_corr)
        else:
            print("No valid target column found from self.target.")
    
        # Save CSV if requested
        if save_csv:
            corr.to_csv(save_csv)
    
        # Return both the full matrix and the target column (if available)
        return corr, target_corr
    
    # Variance Analysis - Identifies features with low variances, which tend to carry little information
    def VarAnalysis(self, threshold=0.01):
        print("\n Low Variance Features:")
        variances = self.df.var()
        low_var = variances[variances < threshold]
        return low_var
    
    # Varianc Inflation Factor -  quantites how much a feature's variance is inflated due to multicollinearity
    def VIF(self, target_col=None, round_to=3, save_csv=None):
        """
        Compute VIF for predictor features (excludes target).
        VIF ≈ 1: low collinearity, >5: moderate, >10: high (rule of thumb).
        """
        if self.df is None or self.df.empty:
            raise ValueError("No data available in self.df.")
    
        # determine target column
        tgt = target_col or getattr(self, "target_key", None)
    
        X = self.df.select_dtypes(include=[np.number]).copy()
        if tgt in X.columns:
            X = X.drop(columns=[tgt])
    
        # drop rows with NaNs and columns with zero variance (avoid crashes / infs)
        X = X.dropna()
        const_cols = [c for c in X.columns if X[c].var(ddof=1) == 0]
        if const_cols:
            X = X.drop(columns=const_cols)
    
        if X.shape[1] == 0:
            print("No predictors available for VIF after dropping target/constant columns.")
            return pd.DataFrame(columns=["Feature", "VIF"])
    
        # compute VIF
        vif_vals = []
        cols = X.columns.tolist()
        for i in range(len(cols)):
            try:
                v = variance_inflation_factor(X.values, i)
            except Exception:
                v = np.inf
            vif_vals.append(v)
    
        vif_df = (pd.DataFrame({"Feature": cols, "VIF": vif_vals})
                    .sort_values("VIF", ascending=False)
                    .reset_index(drop=True))
        
        # Save CSV if requested
        if save_csv:
            vif_df.to_csv(save_csv, index=False)
    
        return vif_df 
    
    # Feature Redundancy
    def FeatRedundancy(self, threshold=0.95, method='pearson',
                       exclude_target=True, round_to=3):
        """
        Print highly correlated feature pairs (> threshold) as a markdown table.
        Returns a DataFrame with columns: feature_a, feature_b, abs_corr.
        """
        if self.df is None or self.df.empty:
            raise ValueError("No data available in self.df.")
    
        # numeric-only
        num_df = self.df.select_dtypes(include=[np.number]).copy()
    
        # determine target column (use self.target_key if you set it in __init__)
        tgt = getattr(self, "target_key", None)
        if tgt is None:
            try:
                tgt = next(
                    (k for k, v in self.raster_folders.items()
                     if v == getattr(self, "target", None)), None
                )
            except Exception:
                tgt = None
    
        if exclude_target and tgt in num_df.columns:
            num_df = num_df.drop(columns=[tgt])
    
        if num_df.shape[1] < 2:
            print("Not enough features to compute pairwise correlations.")
            return pd.DataFrame(columns=["feature_a", "feature_b", "abs_corr"])
    
        method = str(method).lower()
        if method not in ("pearson", "spearman", "kendall"):
            method = "pearson"
    
        corr = num_df.corr(method=method).abs()
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    
        pairs = [
            (r, c, float(upper.loc[r, c]))
            for c in upper.columns for r in upper.index
            if pd.notna(upper.loc[r, c]) and upper.loc[r, c] > threshold
        ]
    
        if pairs:
            print(f"\n Highly Correlated Features (> {threshold}):")
            out_df = (pd.DataFrame(pairs, columns=["feature_a", "feature_b", "abs_corr"])
                        .sort_values("abs_corr", ascending=False)
                        .reset_index(drop=True))
            
            # Print as markdown (fallback to plain print if markdown not available)
            try:
                print(out_df.round({"abs_corr": round_to}).to_markdown(index=False))
            except Exception:
                print(out_df.round({"abs_corr": round_to}))
            return out_df
        else:
            print(f"No highly correlated feature pairs exceed the threshold ({threshold}) using {method}.")
            return pd.DataFrame(columns=["feature_a", "feature_b", "abs_corr"])
    
    #  VISUALIZATIONS
    
    # Plot BoxPlots
    def BoxPlot(self, columns=None, exclude_target=False, whisker_k=1.5, round_to=3):
        """
        Boxplot-based outlier visualization + IQR outlier summary.
    
        Parameters
        ----------
        columns : list[str] or None
            Subset of columns to plot; default = all numeric columns.
        exclude_target : bool
            If True, drop the target column from plots.
        whisker_k : float
            IQR multiplier (1.5 is standard Tukey rule).
        round_to : int
            Rounding for the summary table.
        """
        if self.df is None or self.df.empty:
            raise ValueError("No data available in self.df.")
    
        # Choose columns
        num_df = self.df.select_dtypes(include=[np.number]).copy()
        tgt = getattr(self, "target_key", None)
        if exclude_target and tgt in num_df.columns:
            num_df = num_df.drop(columns=[tgt])
        if columns:
            cols = [c for c in columns if c in num_df.columns]
        else:
            cols = list(num_df.columns)
    
        if not cols:
            print("No numeric columns to plot.")
            return pd.DataFrame(columns=["feature","n","outliers","pct_outliers","q1","q3","iqr","lower_thr","upper_thr"])
    
        # Compute outlier summary (Tukey rule)
        summary_rows = []
        for col in cols:
            s = num_df[col].dropna().values
            if s.size == 0:
                summary_rows.append([col, 0, 0, 0.0, np.nan, np.nan, np.nan, np.nan, np.nan])
                continue
            q1 = np.percentile(s, 25)
            q3 = np.percentile(s, 75)
            iqr = q3 - q1
            lower = q1 - whisker_k * iqr
            upper = q3 + whisker_k * iqr
            out_mask = (s < lower) | (s > upper)
            n = s.size
            n_out = int(out_mask.sum())
            pct = (n_out / n) * 100.0 if n > 0 else 0.0
            summary_rows.append([col, n, n_out, pct, q1, q3, iqr, lower, upper])
    
            # Plot one boxplot per feature
            plt.figure()
            sns.boxplot(x=num_df[col], whis=whisker_k)
            plt.title(f"Boxplot for {col} (whis={whisker_k})")
            plt.grid(True, axis='x')
            plt.tight_layout()
            plt.show()
    
        summary = pd.DataFrame(summary_rows, columns=[
            "feature","n","outliers","pct_outliers","q1","q3","iqr","lower_thr","upper_thr"
        ]).round({"pct_outliers": round_to, "q1": round_to, "q3": round_to,
                  "iqr": round_to, "lower_thr": round_to, "upper_thr": round_to})
    
        # Print markdown table (fallback to plain print if markdown not available)
        print("\nOutlier summary (IQR rule):")
        try:
            print(summary.to_markdown(index=False))
        except Exception:
            print(summary)
    
        return summary

    
    # Distribution of Target/y class
    def yDist(self, target_col=None, bins=30, kde=True,
                       dropna=True, log_x=False, figsize=(8, 4), round_to=3):
        """
        Plot the distribution of the target (numeric: histogram+kde; categorical: bar),
        and print a markdown summary table. Returns the summary (DataFrame/Series).
        """
        if self.df is None or self.df.empty:
            raise ValueError("No data available in self.df.")
    
        # Infer target column if not provided
        if target_col is None:
            target_col = getattr(self, "target_key", None)
            if target_col is None:
                try:
                    target_col = next(
                        (k for k, v in self.raster_folders.items()
                         if v == getattr(self, "target", None)), None
                    )
                except Exception:
                    target_col = None
    
        if not target_col or target_col not in self.df.columns:
            raise ValueError("Target column not found. Set self.target_key or pass target_col.")
    
        s = self.df[target_col]
        if dropna:
            s = s.dropna()
    
        # Numeric target → histogram
        if pd.api.types.is_numeric_dtype(s):
            plt.figure(figsize=figsize)
            sns.histplot(s, bins=bins, kde=kde)
            if log_x:
                plt.xscale('log')
            plt.title(f'Histogram of {target_col}')
            plt.grid(True, axis='y')
            plt.tight_layout()
            plt.show()
    
            desc = s.describe(percentiles=[0.25, 0.5, 0.75]).to_frame(name=target_col).T
            desc["skew"] = s.skew()
            desc["kurtosis"] = s.kurtosis()
            cols = ["count","mean","std","min","25%","50%","75%","max","skew","kurtosis"]
            desc = desc[[c for c in cols if c in desc.columns]].round(round_to)
    
            print("\nSummary stats:")
            try:
                print(desc.to_markdown(index=False))
            except Exception:
                print(desc)
            return desc
    
        # Categorical target → bar chart
        counts = s.astype('category').value_counts(dropna=False)
        plt.figure(figsize=figsize)
        counts.plot(kind='bar')
        plt.title(f'Class Distribution of {target_col}')
        plt.grid(True, axis='y')
        plt.tight_layout()
        plt.show()
    
        out = counts.rename("count").to_frame()
        try:
            print(out.to_markdown())
        except Exception:
            print(out)
        return out
    
    # Distribution of x class
    def XDist(self, columns=None, exclude_target=True,
                               bins=30, kde=True, max_cols=4,
                               per_plot_size=(4, 3)):
        """
        Plot distributions (histograms + optional KDE) for predictor features only.
        No tables, no summaries—just plots.
    
        columns : list[str] or None  -> specific features to plot (default: all numeric predictors)
        exclude_target : bool         -> drop the target column from plots (default True)
        bins : int                    -> histogram bins
        kde : bool                    -> overlay kernel density estimate
        max_cols : int                -> max subplot columns
        per_plot_size : (w,h) inches  -> size per subplot
        """
        if self.df is None or self.df.empty:
            raise ValueError("No data available in self.df.")
    
        # numeric-only
        num_df = self.df.select_dtypes(include=[np.number]).copy()
    
        # infer target column if available
        tgt = getattr(self, "target_key", None)
        if tgt is None:
            try:
                tgt = next((k for k, v in self.raster_folders.items()
                            if v == getattr(self, "target", None)), None)
            except Exception:
                tgt = None
    
        if exclude_target and tgt in num_df.columns:
            num_df = num_df.drop(columns=[tgt])
    
        # choose columns
        if columns:
            cols = [c for c in columns if c in num_df.columns]
        else:
            cols = list(num_df.columns)
    
        if not cols:
            print("No numeric predictor columns to plot.")
            return
    
        # grid sizing
        import math
        n = len(cols)
        ncols = min(max_cols, n)
        nrows = math.ceil(n / ncols)
        fig_w = per_plot_size[0] * ncols
        fig_h = per_plot_size[1] * nrows
    
        fig, axes = plt.subplots(nrows, ncols, figsize=(fig_w, fig_h), squeeze=False)
        axes_flat = axes.ravel()
    
        # draw plots
        for i, col in enumerate(cols):
            s = num_df[col].dropna()
            sns.histplot(s, bins=bins, kde=kde, ax=axes_flat[i])
            axes_flat[i].set_title(col)
            axes_flat[i].grid(True, axis='y')
    
        # hide unused axes
        for j in range(i + 1, len(axes_flat)):
            axes_flat[j].axis('off')
    
        plt.tight_layout()
        plt.show()
    
    #Feature Importance
    def FeatImportance(
        self,
        method: str = "rf",                 # "rf", "xgb", or "shap"
        target_col: str = None,             # defaults to self.target_key
        sample_size: int = 10_000,
        plot: bool = True,                  # bar plot of importances
        shap_summary: bool = False,         # SHAP: also show beeswarm & bar summary
        model_params: dict = None,          # pass through to RF/XGB
        return_model: bool = False,         # optionally return fitted model
        random_state: int = 42
    ):
        """
        Unified feature-importance interface.
    
        method:      "rf" | "xgb" | "shap"
        target_col:  Name of target column (defaults to self.target_key)
        sample_size: Row sample for speed; uses all rows if smaller than dataset
        plot:        Draw a bar chart of importances (RF/XGB/SHAP mean |value|)
        shap_summary:For method='shap', also show SHAP bar + beeswarm summary plots
        model_params:Dict of extra params to pass to the underlying model
        return_model:Return the fitted model (and SHAP objects when method='shap')
        random_state:Reproducibility for sampling / RF / XGB
        """
    
        # Select Target/y 
        if target_col is None:
            target_col = getattr(self, "target_key", None)
        if self.df is None or target_col not in self.df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataframe.")
    
        # Build X, y 
        X = self.df.drop(columns=[target_col])
        y = self.df[target_col]
    
        # Sample if requested 
        if sample_size < len(X):
            X = X.sample(sample_size, random_state=random_state)
            y = y.loc[X.index]
    
        # Defaults per model 
        model_params = model_params or {}
        method = method.lower().strip()
        valid = {"rf", "random_forest", "xgb", "xgboost", "shap"}
        if method not in valid:
            raise ValueError(f"'method' must be one of {valid}")
    
        # Train + compute importances
        fitted_model = None
        shap_values = None
        explainer = None
    
        if method in {"rf", "random_forest"}:
            # Random Forest
            defaults = dict(n_estimators=300, n_jobs=-1, random_state=random_state)
            defaults.update(model_params)
            model = RandomForestRegressor(**defaults)
            model.fit(X, y)
            fitted_model = model
    
            importances = model.feature_importances_
            imp_name = "Importance"
    
        elif method in {"xgb", "xgboost"}:
            # XGBoost
            defaults = dict(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=random_state,
                n_jobs=-1
            )
            defaults.update(model_params)
            model = XGBRegressor(**defaults)
            model.fit(X, y)
            fitted_model = model
    
            importances = model.feature_importances_  # (gain-based by default)
            imp_name = "Importance"
    
        else:  # method == "shap"
            # Use XGB as the default SHAP-backed model (fast TreeExplainer)
            defaults = dict(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=random_state,
                n_jobs=-1
            )
            defaults.update(model_params)
            model = XGBRegressor(**defaults)
            model.fit(X, y)
            fitted_model = model
    
            # SHAP values (TreeExplainer for XGB)
            explainer = shap.TreeExplainer(model, X)
            shap_values = explainer(X)
    
            # Mean absolute SHAP importance per feature
            importances = np.abs(shap_values.values).mean(axis=0)
            imp_name = "SHAP Importance"
    
        # Assemble importance table
        importance_df = pd.DataFrame(
            {"Feature": X.columns, imp_name: importances}
        ).sort_values(by=imp_name, ascending=False).reset_index(drop=True)
    
        # Plot (bar chart) 
        if plot:
            plt.figure(figsize=(10, max(4, 0.4 * len(importance_df))))
            sns.barplot(
                data=importance_df,
                x=imp_name,
                y="Feature",
                orient="h"
            )
            title_map = {
                "rf": "Random Forest Feature Importances",
                "random_forest": "Random Forest Feature Importances",
                "xgb": "XGBoost Feature Importances",
                "xgboost": "XGBoost Feature Importances",
                "shap": "SHAP Mean |Value| (Global Importance)"
            }
            plt.title(title_map[method])
            plt.tight_layout()
            plt.show()
    
        # Optional SHAP summary plots 
        if method == "shap" and shap_summary:
            shap.summary_plot(shap_values, X, plot_type="bar", show=True)
            shap.summary_plot(shap_values, X, show=True)
    
        # Return
        if return_model:
            # Return richer objects for downstream use
            return {
                "importance_df": importance_df,
                "model": fitted_model,
                "shap_values": shap_values,
                "explainer": explainer
            }
        return importance_df