
"""
Created on Mon Aug 25 16:28:09 2025

@author: Jeffrey Blay
"""
# IMPORT LIBRARIES
import os
import numpy as np
import rasterio
from tensorflow.keras.utils import Sequence

# CLASS WITH FUNCTIONS FOR DATASETS LOADING
class Implement:
    
    # Function to load tiles for model training
    def LoadTiles(feature_folders, target_folder, size=(256, 256),extensions=(".tif", ".tiff"),
        dtype=np.float32):
        
        # Helper: list valid tile names in a folder
        def list_names(folder):
            return {
                f for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(extensions)
            }
    
        if not feature_folders:
            raise ValueError("feature_folders cannot be empty.")
    
        # Intersection of filenames across all feature folders AND the target
        common = None
        for _, folder in feature_folders.items():
            names = list_names(folder)
            common = names if common is None else (common & names)
        common = (common & list_names(target_folder)) if common else set()
    
        if not common:
            print("No common filenames across features and target.")
            return (None, None) 
    
        channel_names = list(feature_folders.keys())
        X_list, y_list = [], []
    
        for fn in sorted(common):
            # Read features
            channels, bad = [], False
            for key in channel_names:
                fpath = os.path.join(feature_folders[key], fn)
                with rasterio.open(fpath) as src:
                    arr = src.read(1)
                    if size and arr.shape != size:
                        bad = True
                        break
                    channels.append(arr)
    
            if bad:
                # Skip tiles with mismatched shapes
                continue
    
            # Read target
            tpath = os.path.join(target_folder, fn)
            with rasterio.open(tpath) as src:
                tgt = src.read(1)
                if size and tgt.shape != size:
                    continue
    
            X_list.append(np.stack(channels, axis=-1))
            y_list.append(tgt)
    
        if not X_list:
            print("No valid pairs after size checks.")
            return (None, None) 
    
        X = np.asarray(X_list, dtype=dtype)                    # (N, H, W, C)
        y = np.expand_dims(np.asarray(y_list, dtype=dtype), -1) # (N, H, W, 1)
    
        print(f"Loaded {X.shape[0]} samples | X: {X.shape}  y: {y.shape} | Channels: {channel_names}")
    
        return X, y
    
    
    # Function to shuffle and split tiles into train, validation and test tiles
    def ShuffleSplit(X, y, train_size: float = 0.6, val_size: float = 0.2, test_size: float | None = 0.2,
        seed: int = 42, shuffle: bool = True, verbose: bool = True):

        assert len(X) == len(y), "X and y must have the same length."
        n = len(X)
    
        # Fill in test_size if omitted
        if test_size is None:
            test_size = 1.0 - train_size - val_size
    
        # Validate fractions
        total = train_size + val_size + test_size
        if not np.isclose(total, 1.0, atol=1e-8):
            raise ValueError(f"train+val+test must sum to 1. Got {total:.6f}.")
        if any(p < 0 for p in (train_size, val_size, test_size)):
            raise ValueError("Fractions must be non-negative.")
    
        # Shuffle indices
        idx = np.arange(n)
        if shuffle:
            rng = np.random.RandomState(seed)
            rng.shuffle(idx)
    
        Xs, ys = X[idx], y[idx]
    
        # Convert fractions to counts (floor first; leftover goes to test)
        n_train = int(np.floor(n * train_size))
        n_val   = int(np.floor(n * val_size))
        n_test  = n - n_train - n_val  # ensures sums to N
        
        if n_test <0:
            raise ValueError("Split sizes produce negative test count. Adjust fractions.")
    
        X_train, y_train = Xs[:n_train], ys[:n_train]
        X_val,   y_val   = Xs[n_train:n_train + n_val], ys[n_train:n_train + n_val]
        X_test,  y_test  = Xs[n_train + n_val:], ys[n_train + n_val:]
    
        if verbose:
            pct = lambda k: f"{100*k/n:.1f}%" if n > 0 else "0.0%"
            print(f"Train: {X_train.shape}, {y_train.shape}  ({pct(len(X_train))})")
            print(f"Val:   {X_val.shape}, {y_val.shape}      ({pct(len(X_val))})")
            print(f"Test:  {X_test.shape}, {y_test.shape}    ({pct(len(X_test))})")
    
        return X_train, y_train, X_val, y_val, X_test, y_test


    # Simple data pipeline class for preparing data for model loading
    # Simple data pipeline that creates batches for training, with the option of data augmentation (geometry)
    class SimplePipeline(Sequence):
        """
        Geometry-only augmentation options (strings): 
        'hflip', 'vflip', 'rot90', 'rot180', 'rot270', 'transpose'
        """
        def __init__(self, X, y, batch_size=32, shuffle=True,
                     augment=False, aug_ops=('hflip','vflip','rot90','rot270','transpose'),
                     aug_prob=0.5, seed=None):
            self.X, self.y = X, y
            self.batch_size, self.shuffle = batch_size, shuffle
            self.augment, self.aug_ops, self.aug_prob = augment, tuple(aug_ops), aug_prob
            self.rng = np.random.default_rng(seed)
            self.indexes = np.arange(len(X))
            if self.shuffle: self.rng.shuffle(self.indexes)
    
        def __len__(self):
            return (len(self.X) + self.batch_size - 1) // self.batch_size
    
        def __getitem__(self, idx):
            inds = self.indexes[idx*self.batch_size:(idx+1)*self.batch_size]
            batch_X = self.X[inds].copy()
            batch_y = self.y[inds].copy()
            
            if self.augment and self.aug_ops:
                for i in range(len(inds)):
                    if self.rng.random() < self.aug_prob:
                        batch_X[i], batch_y[i] = self._apply_aug(batch_X[i], batch_y[i])
            return batch_X, batch_y
    
        def on_epoch_end(self):
            if self.shuffle: self.rng.shuffle(self.indexes)
    
        # ---- helpers ----
        def _apply_aug(self, img, mask):
            op = self.rng.choice(self.aug_ops)
            if   op == 'hflip':   return np.flip(img, 1), np.flip(mask, 1)
            elif op == 'vflip':   return np.flip(img, 0), np.flip(mask, 0)
            elif op == 'rot90':   return np.rot90(img, 1, (0,1)), np.rot90(mask, 1, (0,1))
            elif op == 'rot180':  return np.rot90(img, 2, (0,1)), np.rot90(mask, 2, (0,1))
            elif op == 'rot270':  return np.rot90(img, 3, (0,1)), np.rot90(mask, 3, (0,1))
            elif op == 'transpose':
                perm = (1, 0) + tuple(range(2, img.ndim))
                return np.transpose(img, perm), np.transpose(mask, perm)
            return img, mask    
    