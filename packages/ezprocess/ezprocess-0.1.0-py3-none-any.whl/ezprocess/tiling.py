
"""
Created on Fri Aug 22 14:46:00 2025

@author: Jeffrey Blay
"""
# IMPORT LIBRARIES
import os
import random
import shutil
import rasterio
import numpy as np
from shutil import copy2
import matplotlib.pyplot as plt
from rasterio.windows import Window
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

# CLASS WITH FUNCTIONS FOR TILING
class Tiles:
    
    # Function to create Consistent tiles                            
    def CreateTiles(input_folders, output_folders, tile_size=(256, 256), overlap=0, reference_key='depth'):
        """
        Create overlapping tiles consistently across aligned rasters.
    
        Parameters:
            input_folders (dict): Input folders keyed by dataset types (e.g., 'img', 'dem', 'extent', 'depth').
            output_folders (dict): Output folders keyed by 'out_' + dataset type.
            tile_size (tuple): Width, height of each tile (default: (256, 256)).
            overlap (int): Number of pixels to overlap tiles by (default: 0).
            reference_key (str): Dataset key to use as reference for tiling (default: 'depth').
        """
        tile_width, tile_height = tile_size
        stride_x = tile_width - overlap
        stride_y = tile_height - overlap
    
        ref_folder = input_folders[reference_key]
        stats = {}  # store the number of tiles created per file
        
        for file_name in os.listdir(ref_folder):
            if not file_name.endswith(".tif"):
                continue
            
            print(f"\nProcessing file: {file_name}")
            stats[file_name] = {}
    
            # Open reference raster
            ref_path = os.path.join(ref_folder, file_name)
            with rasterio.open(ref_path) as ref_src:
                width, height = ref_src.width, ref_src.height
                windows = []
    
                for i in range(0, width - tile_width + 1, stride_x):
                    for j in range(0, height - tile_height + 1, stride_y):
                        windows.append((Window(i, j, tile_width, tile_height), i, j))
    
            # Now apply windows to all rasters
            for key in input_folders:
                input_path = os.path.join(input_folders[key], file_name)
                output_path_folder = output_folders[f"out_{key}"]
                os.makedirs(output_path_folder, exist_ok=True)
                
                tile_count = 0
                with rasterio.open(input_path) as src:
                    for tile_num, (window, i, j) in enumerate(windows):
                        tile_data = src.read(window=window)
                        tile_name = f"{os.path.splitext(file_name)[0]}_tile_{tile_num}.tif"
                        output_path = os.path.join(output_path_folder, tile_name)
    
                        with rasterio.open(
                            output_path,
                            'w',
                            driver='GTiff',
                            height=tile_height,
                            width=tile_width,
                            count=tile_data.shape[0],
                            dtype=tile_data.dtype,
                            crs=src.crs,
                            transform=rasterio.windows.transform(window, src.transform)
                        ) as dst:
                            dst.write(tile_data)
                        tile_count += 1
                        
                stats[file_name][key] = tile_count
                print(f" {key}: {tile_count} tiles")
                
        return stats
    
    
    # Function to filter tiles based on the selected target
    def FilterTiles(reference_folder, input_folders, output_folders, reference_key='depth', threshold=0.5):
        """
        Filters reference tiles based on the percentage of zero pixels.
        Copies corresponding tiles from other datasets to designated output folders.
        
        Args:
            reference_folder (str): Path to the folder containing reference tiles.
            input_folders (dict): Dictionary of other datasets with keys matching output folders.
            output_folders (dict): Dictionary of output folders for filtered tiles.
            threshold (float): Maximum allowed percentage of null pixels (0-1) for a tile to be retained.
        """
        # Ensure output directories exist
        for folder in output_folders.values():
            os.makedirs(folder, exist_ok=True)
        
        filtered_count = 0
        skipped_count = 0
        ref_out_key = f'out_{reference_key}'
    
        # Process depth tiles
        for file_name in os.listdir(reference_folder):
            if file_name.endswith(".tif"):
                ref_path = os.path.join(reference_folder, file_name)
                
                with rasterio.open(ref_path) as src:
                    ref_data = src.read(1)  # Read the first band of the reference raster
                    
                    # Calculate null ratio
                    total_pixels = ref_data.size
                    zero_pixels = int(np.sum(ref_data == 0))  # identify zero pixels
                    #valid_pixels = total_pixels - zero_pixels
                    zero_ratio = zero_pixels / total_pixels
                    
                    # Debugging output
                    print(f"Processing {file_name}: Total Pixels={total_pixels}, Zero Pixels={zero_pixels}, Zero Ratio={zero_ratio:.2f}")
                    
                    # Check if the tile meets the null threshold
                    if zero_ratio < threshold:
                        filtered_count += 1
                        print(f" ✓ Keeping {file_name}.")
                        
                        
                        # Copy the depth tile to the output folder
                        if ref_out_key in output_folders:
                            copy2(ref_path, os.path.join(output_folders[ref_out_key], file_name))
                        else:
                            print(f" Warning: '{ref_out_key}' not found in output_folder; skipping reference copy")
                        
                        
                        # Copy corresponding tiles in other datasets
                        for key, input_folder in input_folders.items():
                            input_path = os.path.join(input_folder, file_name)
                            out_key = f"out_{key}"
                            if out_key not in output_folders:
                                print(f" Warning: '{out_key}' not found in output_folders for dataset '{key}'.")
                                continue
                            if os.path.exists(input_path):
                                copy2(input_path, os.path.join(output_folders[out_key], file_name))
                            else:
                                print(f"  Warning: {file_name} not found in dataset '{key}'.")
                    else:
                        skipped_count += 1
                        print(f"Tile {file_name} skipped due to high zero ratio ({zero_ratio:.2f}).")
        
        # Summary
        print(f"\nTotal filtered tiles: {filtered_count}")
        print(f"Total skipped tiles: {skipped_count}")
  

                            
    # Function to sample tiles
    def SampleTiles(input_folders, output_folders, ref_key='depth', sample_size=500):
        """
        Randomly sample corresponding tiles from filtered/all tiles and save them to output folders.
    
        Parameters:
            input_folders (dict): Dictionary containing folder paths of tiles repositories to sample from.                                     Keys should be 'dem', 'extent', 'img', 'depth'.
            output_folders (dict): Dictionary containing sample folder paths for each dataset.
                                   Keys should be 'out_dem', 'out_extent', 'out_img', 'out_depth'.
            sample_size (int): Number of samples to select (default is 200).
        """
        # Get the list of filtered tile names from the reference folder
        ref_folder = input_folders[ref_key]
        all_tiles = [f for f in os.listdir(ref_folder) if f.endswith('.tif')]
        
        # Ensure the number of samples does not exceed the available tiles
        if len(all_tiles) < sample_size:
            raise ValueError(f"Not enough filtered tiles to sample {sample_size}. Only {len(all_tiles)} tiles are available.")
        
        # Randomly select the sample tiles
        sampled_tiles = random.sample(all_tiles, sample_size)
        
        # Ensure sample directories exist
        for folder in output_folders.values():
            if not os.path.exists(folder):
                os.makedirs(folder)
        
        # Copy sampled tiles and their corresponding ones to sample folders
        for tile_name in sampled_tiles:
            for key, input_folder in input_folders.items():
                input_path = os.path.join(input_folder, tile_name)
                output_folder = output_folders[f"out_{key}"]
                output_path = os.path.join(output_folder, tile_name)
                shutil.copy2(input_path, output_path)
        
        print(f"Successfully sampled {sample_size} tiles and saved them to the sample folders.")
        
    # Function to visualize tiles    
    def VisualizeTiles(folder_paths, num_samples=1, figsize_per_tile=(4, 4), cmap='viridis'):
        """
        Visualize matching tiles with a cleanly placed colorbar for scalar rasters.
    
        Parameters:
            folder_paths (dict): Dict with category names as keys and folder paths as values.
            num_samples (int): Number of matching tile samples to visualize.
            figsize_per_tile (tuple): Size of each subplot (width, height).
            cmap (str): Colormap for non-RGB data.
        """
        # Get only matching tiles across all categories
        tile_sets = [set(f for f in os.listdir(path) if f.endswith('.tif')) for path in folder_paths.values()]
        common_tiles = set.intersection(*tile_sets)
    
        if not common_tiles:
            print("No matching tiles found across all folders.")
            return
    
        selected_tiles = random.sample(list(common_tiles), min(num_samples, len(common_tiles)))
        categories = list(folder_paths.keys())
        
        # Create figure and axes
        fig_width = figsize_per_tile[0] * len(categories)
        fig_height = figsize_per_tile[1] * num_samples
        fig, axes = plt.subplots(nrows=num_samples, ncols=len(categories), figsize=(fig_width, fig_height))
        if num_samples == 1:
            axes = np.expand_dims(axes, axis=0)
    
        # Get global vmin/vmax for scalar categories
        vmin, vmax = float('inf'), float('-inf')
        scalar_categories = [cat for cat in categories if cat != 'imagery']
        for cat in scalar_categories:
            for tile in selected_tiles:
                with rasterio.open(os.path.join(folder_paths[cat], tile)) as src:
                    data = src.read(1)
                    vmin = min(vmin, np.nanmin(data))
                    vmax = max(vmax, np.nanmax(data))
    
        # Plot tiles
        for i, tile in enumerate(selected_tiles):
            for j, category in enumerate(categories):
                path = os.path.join(folder_paths[category], tile)
                ax = axes[i, j]
                with rasterio.open(path) as src:
                    if category == 'imagery':
                        rgb = np.stack([src.read(b) for b in [1, 2, 3]], axis=-1)
                        ax.imshow(rgb)
                    else:
                        data = src.read(1)
                        ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
                    ax.set_title(f"{category.upper()}", fontsize=8)
                    ax.axis('off')
    
        # Add a dedicated colorbar outside the figure
        cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  # [left, bottom, width, height]
        sm = ScalarMappable(norm=Normalize(vmin=vmin, vmax=vmax), cmap=cmap)
        cbar = plt.colorbar(sm, cax=cbar_ax)
        cbar.set_label('Low ← Value → High', fontsize=10)
    
        plt.subplots_adjust(right=0.9, wspace=0.05, hspace=0.2)
        plt.show()
                        
              