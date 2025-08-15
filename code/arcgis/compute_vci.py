"""
compute_vci.py
Requirements: rasterio, numpy, tqdm
Usage: python compute_vci.py
"""

import os
import re
import glob
import numpy as np
import rasterio
from rasterio.windows import Window
from tqdm import tqdm

# -------- CONFIG ----------
ndvi_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\NDVI_Data_2013FEB_2025JUL\NDVI_TIF\Clipped_NDVI_Real"
out_stats_folder = os.path.join(ndvi_folder, "NDVI_Historical_Stats_v2")
out_vci_folder = os.path.join(ndvi_folder, "NDVI_VCI")
os.makedirs(out_stats_folder, exist_ok=True)
os.makedirs(out_vci_folder, exist_ok=True)

# filename pattern and regex to extract date
pattern = re.compile(r"NDVI_(\d{4})_(\d{2})_(\d{2})\.tif$")

# Historical baseline years
hist_start = 2013
hist_end = 2022

# Gather NDVI files
all_files = sorted(glob.glob(os.path.join(ndvi_folder, "real_clipped_NDVI_*.tif")))
if not all_files:
    raise SystemExit("No NDVI files found in folder")

# Open one file to get metadata
with rasterio.open(all_files[0]) as src0:
    meta = src0.meta.copy()
    width = src0.width
    height = src0.height
    dtype = src0.dtypes[0]
    nodata = src0.nodata if src0.nodata is not None else -9999
    transform = src0.transform
    crs = src0.crs

# Group historical files by month
hist_by_month = {f"{m:02d}": [] for m in range(1, 13)}
target_files = []  # files to compute VCI for (e.g., 2023-2025)
for fp in all_files:
    m = pattern.search(os.path.basename(fp))
    if not m:
        continue
    year = int(m.group(1))
    month = m.group(2)
    if hist_start <= year <= hist_end:
        hist_by_month[month].append(fp)
    else:
        # treat as target (we'll compute VCI for these)
        target_files.append(fp)

# Function to compute per-month min/max using block processing
def compute_month_minmax(month, files, out_min, out_max):
    """Compute pixel-wise min and max across list of files"""
    if os.path.exists(out_min) and os.path.exists(out_max):
        print("Existing stats found:", out_min, out_max)
        return
    print(f"Computing min/max for month {month} ({len(files)} files)...")
    # initialize arrays with +inf and -inf
    meta_local = meta.copy()
    meta_local.update(driver="GTiff", dtype="float32", nodata=np.float32(nodata), count=1)
    # create temp writers to write block by block
    block_shape = 512  # tune if necessary
    with rasterio.open(out_min, "w", **meta_local) as min_dst, \
         rasterio.open(out_max, "w", **meta_local) as max_dst:
        for ji, window in tqdm(list(rasterio.windows.Window.col_off_rows(0, width, height, block_shape))):
            # window is a tuple? easier: iterate by rows/cols manually
            pass

# Simpler block iteration helper
def iter_windows(src, blocksize=512):
    for top in range(0, src.height, blocksize):
        h = min(blocksize, src.height - top)
        for left in range(0, src.width, blocksize):
            w = min(blocksize, src.width - left)
            yield Window(left, top, w, h)

# Implement compute month using windows
for month, files in hist_by_month.items():
    if not files:
        print(f"No historical files for month {month}, skipping.")
        continue
    out_min = os.path.join(out_stats_folder, f"NDVI_min_{month}.tif")
    out_max = os.path.join(out_stats_folder, f"NDVI_max_{month}.tif")
    if os.path.exists(out_min) and os.path.exists(out_max):
        print("Stats for month", month, "already exist.")
        continue

    # prepare output files
    meta_local = meta.copy()
    meta_local.update(dtype="float32", count=1, nodata=np.float32(nodata), compress="lzw")
    with rasterio.open(out_min, "w", **meta_local) as dst_min, rasterio.open(out_max, "w", **meta_local) as dst_max:
        # iterate windows
        for window in iter_windows(rasterio.open(files[0])):
            # initialize arrays
            min_block = None
            max_block = None
            for fp in files:
                with rasterio.open(fp) as src:
                    arr = src.read(1, window=window).astype("float32")
                    # set nodata to nan for proper min/max
                    arr[arr == nodata] = np.nan
                    if min_block is None:
                        min_block = arr.copy()
                        max_block = arr.copy()
                    else:
                        # element-wise nanmin and nanmax
                        min_block = np.fmin(min_block, arr)
                        max_block = np.fmax(max_block, arr)
            # replace nan back to nodata
            min_block[np.isnan(min_block)] = nodata
            max_block[np.isnan(max_block)] = nodata
            dst_min.write(min_block, 1, window=window)
            dst_max.write(max_block, 1, window=window)
    print(f"Saved NDVI_min_{month}, NDVI_max_{month}")

# Now compute VCI for target files
print("Computing VCI for target files (count):", len(target_files))
for fp in target_files:
    bn = os.path.basename(fp)
    m = pattern.search(bn)
    if not m:
        continue
    month = m.group(2)
    ndvimin = os.path.join(out_stats_folder, f"NDVI_min_{month}.tif")
    ndvimax = os.path.join(out_stats_folder, f"NDVI_max_{month}.tif")
    if not os.path.exists(ndvimin) or not os.path.exists(ndvimax):
        print("Missing min/max for month", month, "skip", bn)
        continue

    out_vci = os.path.join(out_vci_folder, f"VCI_{m.group(1)}_{month}_{m.group(3)}.tif")
    if os.path.exists(out_vci):
        print("VCI exists:", out_vci)
        continue

    # compute block by block
    with rasterio.open(fp) as src_ndvi, rasterio.open(ndvimin) as src_min, rasterio.open(ndvimax) as src_max:
        meta_vci = src_ndvi.meta.copy()
        meta_vci.update(dtype="float32", nodata=np.float32(nodata))
        with rasterio.open(out_vci, "w", **meta_vci) as dst:
            for window in iter_windows(src_ndvi):
                a = src_ndvi.read(1, window=window).astype("float32")
                b = src_min.read(1, window=window).astype("float32")
                c = src_max.read(1, window=window).astype("float32")
                a[a == nodata] = np.nan
                b[b == nodata] = np.nan
                c[c == nodata] = np.nan
                denom = (c - b)
                # avoid division by zero
                with np.errstate(invalid='ignore', divide='ignore'):
                    vci = 100.0 * (a - b) / denom
                # set where denom == 0 or any nan -> nodata
                vci[np.isnan(vci)] = nodata
                vci[np.isinf(vci)] = nodata
                dst.write(vci.astype("float32"), 1, window=window)
    print("Saved VCI:", out_vci)

print("VCI computation finished.")
