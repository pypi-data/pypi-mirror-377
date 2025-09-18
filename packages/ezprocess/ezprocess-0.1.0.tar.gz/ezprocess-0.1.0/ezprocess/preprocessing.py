
"""
Created on Thu Aug 21 17:56:24 2025

@author: Jeffrey Blay
"""

# IMPORT LIBRARIES
import os
import rasterio
import numpy as np
import math
import laspy 
from rasterio.transform import from_origin
from rasterio.crs import CRS


# CLASS WITH FUNCTIONS FOR DATA PROCESSING
class PreProcess:
    
    # Function to create DEM, DSM, and nDSM from lidar data
    def SimpleLidar(input_folder, output_folder, epsg, products=("DEM","DSM","nDSM"), cellsize=1.0):
        """
        Super-simple LiDAR gridding to DEM/DSM/nDSM 
        - DEM = mean of class 2 (ground) per cell
        - DSM = max of first returns per cell
        - nDSM = DSM - DEM
        Requires: laspy, numpy, rasterio
        """
        os.makedirs(output_folder, exist_ok=True)
        # 1) find files
        files = [os.path.join(r,f) for r,_,fs in os.walk(input_folder)
                 for f in fs if f.lower().endswith((".las",".laz"))]
        if not files: raise RuntimeError("No LAS/LAZ found.")
        # 2) extent from headers
        xmin=ymin=np.inf; xmax=ymax=-np.inf
        for p in files:
            with laspy.open(p) as lf:
                h=lf.header
                xmin=min(xmin,h.mins[0]); ymin=min(ymin,h.mins[1])
                xmax=max(xmax,h.maxs[0]); ymax=max(ymax,h.maxs[1])
        width=int(math.ceil((xmax-xmin)/cellsize)); height=int(math.ceil((ymax-ymin)/cellsize))
        if width<=0 or height<=0: raise RuntimeError("Bad grid size—check cellsize.")
        transform=from_origin(xmin, ymax, cellsize, cellsize); crs=CRS.from_epsg(int(epsg))
        base=os.path.basename(os.path.normpath(input_folder)); N=height*width
        # 3) accumulators
        dem_sum=np.zeros(N, np.float64); dem_cnt=np.zeros(N, np.uint32)     # DEM mean
        dsm_max=np.full(N, -np.inf, np.float64)                             # DSM max
        def rc_idx(x,y):
            c=((x-xmin)/cellsize).astype(np.int64); r=((ymax-y)/cellsize).astype(np.int64)
            m=(c>=0)&(c<width)&(r>=0)&(r<height); return r[m], c[m], m
        # 4) bin points (reads full file for simplicity)
        for p in files:
            pts = laspy.read(p)
            x,y,z = pts.x, pts.y, pts.z
            # DEM: class 2
            m = (pts.classification == 2)
            if np.any(m):
                r,c,keep = rc_idx(x[m], y[m]); idx = r*width + c
                np.add.at(dem_sum, idx, z[m][keep]); np.add.at(dem_cnt, idx, 1)
            # DSM: first return
            m = (pts.return_number == 1)
            if np.any(m):
                r,c,keep = rc_idx(x[m], y[m]); idx = r*width + c
                np.maximum.at(dsm_max, idx, z[m][keep])
        # 5) finalize arrays
        dem=np.full(N, np.nan, np.float32); ok=(dem_cnt>0); dem[ok]=(dem_sum[ok]/dem_cnt[ok]).astype(np.float32)
        dsm=dsm_max.astype(np.float32); dsm[np.isneginf(dsm)]=np.nan
        dem=dem.reshape(height,width); dsm=dsm.reshape(height,width)
        ndsm=(dsm - dem).astype(np.float32); ndsm[np.isnan(dsm)|np.isnan(dem)]=np.nan
        # 6) write requested
        def write_tif(path, A):
            prof=dict(driver="GTiff", height=A.shape[0], width=A.shape[1], count=1,
                      dtype="float32", crs=crs, transform=transform, nodata=-9999.0,
                      tiled=True, compress="deflate")
            out=np.where(np.isnan(A), -9999.0, A).astype(np.float32)
            with rasterio.open(path, "w", **prof) as dst: dst.write(out,1)
        out={}
        if isinstance(products, str) and products.lower()=="all": products=("DEM","DSM","nDSM")
        if "DEM" in products: out["DEM"]=os.path.join(output_folder, f"{base}_DEM.tif"); write_tif(out["DEM"], dem)
        if "DSM" in products: out["DSM"]=os.path.join(output_folder, f"{base}_DSM.tif"); write_tif(out["DSM"], dsm)
        if "nDSM" in products: out["nDSM"]=os.path.join(output_folder, f"{base}_nDSM.tif"); write_tif(out["nDSM"], ndsm)
        return out
    
    
    #Function to identify the global maximum and minimum values from data-wide rasters in folder paths
    def GlobRange(folder_path):
        global_max = -np.inf
        global_min = np.inf

        for filename in os.listdir(folder_path):
            if filename.endswith('.tif'):
                filepath = os.path.join(folder_path, filename)
                with rasterio.open(filepath) as src:
                    depth_data = src.read(1)
                    
                    # Find local min and max directly
                    local_max = depth_data.max()
                    local_min = depth_data.min()

                    # Update global min and max
                    if local_max > global_max:
                        global_max = local_max
                    if local_min < global_min:
                        global_min = local_min
                        
        return global_max, global_min
    
    
    # Function to normalize (minMax) raster data while preserving NoData (dry areas) Values.
    def MinMaxNorm(input_folder, output_folder, min_value, max_value):
        os.makedirs(output_folder, exist_ok=True)
        
        for file in os.listdir(input_folder):
            if file.endswith('.tif'):
                filepath = os.path.join(input_folder, file)
                with rasterio.open(filepath) as src:
                    data = src.read(1)
                    profile = src.profile
    
                    # Replace NaNs with 0 (i.e., unflooded area)
                    data = np.where(np.isnan(data), 0, data)
                    
                    # Normalize
                    norm_data = (data - min_value) / (max_value - min_value)
                    norm_data = np.clip(norm_data, 0, 1)
    
                    # Set nodata to none (which now represents unflooded/masked)
                    profile.update(dtype=rasterio.float32, nodata=None) # sets nodata to none
    
                    # Write output
                    output_path = os.path.join(output_folder, f'MinMaxNorm_{file}')
                    with rasterio.open(output_path, 'w', **profile) as dst:
                        dst.write(norm_data.astype(np.float32), 1)
    
                print(f"Normalized and saved: {output_path}")
                
    # Function to normalize RGB rasters, with three channels
    def NormRGB(input_folder, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        
        # Loop through all files in the input folder
        for file in os.listdir(input_folder):
            if file.endswith(".tif"):
                input_path = os.path.join(input_folder, file)
                output_path = os.path.join(output_folder, f"normalized_{file}")
                
                # Open the input image files
                with rasterio.open(input_path) as src:
                    # Read all bands
                    img_data = src.read()
                    
                    # Normalize each band independently
                    img_data = src.read()
                    
                    # Define metadata for the output file
                    out_meta = src.meta
                    out_meta.update({"dtype": "float32"})
                    
                    # save the normalized image
                    with rasterio.open(output_path, 'w', **out_meta) as dst:
                        dst.write(img_data.astype(np.float32))
                print(f"Normalized and saved: {output_path}")
                
    # Function to apply log(x + 1) transformation to all rasters in folder
    def LogTransform(input_folder, output_folder):
        os.makedirs(output_folder, exist_ok=True)

        for file in os.listdir(input_folder):
            if file.endswith('.tif'):
                filepath = os.path.join(input_folder, file)
                with rasterio.open(filepath) as src:
                    data = src.read(1)
                    profile = src.profile
                    
                    # Apply log1p only to positive values
                    with np.errstate(divide='ignore', invalid='ignore'):
                        transformed = np.where(data >= 0, np.log1p(data), np.nan)

                    profile.update(dtype=rasterio.float32, nodata=np.nan)
                    
                    output_path = os.path.join(output_folder, f'log1p_{file}')
                    with rasterio.open(output_path, 'w', **profile) as dst:
                        dst.write(transformed.astype(np.float32), 1)
                print(f"Log-transformed and saved: {output_path}")
                
                
    # Function to apply cube-root transformation to all rasters in a folder
    def CubeRootTransform(input_folder, output_folder):
        os.makedirs(output_folder, exist_ok=True)

        for file in os.listdir(input_folder):
            if file.endswith('.tif'):
                filepath = os.path.join(input_folder, file)
                with rasterio.open(filepath) as src:
                    data = src.read(1)
                    profile = src.profile

                    # Apply cube root transformation (handles negatives)
                    transformed = np.cbrt(data)

                    profile.update(dtype=rasterio.float32, nodata=np.nan)
                    
                    output_path = os.path.join(output_folder, f'cbrt_{file}')
                    with rasterio.open(output_path, 'w', **profile) as dst:
                        dst.write(transformed.astype(np.float32), 1)
                print(f"Cube-root transformed and saved: {output_path}")
