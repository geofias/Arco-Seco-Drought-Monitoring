import arcpy
import os
import re
import numpy as np
from osgeo import gdal
from scipy.stats import gamma, norm

# ---------------- CONFIG ----------------
chirps_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\Chirps\Clipped_250m"
out_folder = os.path.join(chirps_folder, "SPI1")
os.makedirs(out_folder, exist_ok=True)

# Raster format: clip_chirps-v2.0.2013.02
pattern = r"(\d{4})\.(\d{2})"

baseline_start = 2013
baseline_end   = 2022

# ---------------- HELPER: Read raster to array ----------------
def read_raster_as_array(path):
    ds = gdal.Open(path)
    arr = ds.ReadAsArray().astype(np.float32)
    nodata = ds.GetRasterBand(1).GetNoDataValue()
    if nodata is not None:
        arr[arr == nodata] = np.nan
    gt = ds.GetGeoTransform()
    proj = ds.GetProjection()
    return arr, gt, proj, nodata

# ---------------- HELPER: Save array to raster ----------------
def save_array_as_raster(arr, gt, proj, out_path, nodata):
    driver = gdal.GetDriverByName("GTiff")
    out_ds = driver.Create(out_path, arr.shape[1], arr.shape[0], 1, gdal.GDT_Float32)
    out_ds.SetGeoTransform(gt)
    out_ds.SetProjection(proj)
    band = out_ds.GetRasterBand(1)
    band.WriteArray(arr)
    if nodata is not None:
        band.SetNoDataValue(nodata)
    band.FlushCache()
    out_ds = None

# ---------------- ORGANIZE FILES ----------------
files = [f for f in os.listdir(chirps_folder) if f.endswith(".tif")]
files_info = []
for f in files:
    m = re.search(pattern, f)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        files_info.append((f, year, month))

files_info.sort(key=lambda x: (x[1], x[2]))  # sort by year, month

# Group rasters by month (all years)
by_month = {m: [] for m in range(1, 13)}
for fname, year, month in files_info:
    by_month[month].append((fname, year))

# ---------------- CALCULATE SPI-1 ----------------
for month in range(1, 13):
    # Get baseline rasters for this month
    baseline_files = [fname for fname, year in by_month[month] if baseline_start <= year <= baseline_end]

    # Read all baseline arrays into stack
    baseline_arrays = []
    for bf in baseline_files:
        arr, gt, proj, nodata = read_raster_as_array(os.path.join(chirps_folder, bf))
        baseline_arrays.append(arr)
    baseline_stack = np.stack(baseline_arrays, axis=0)  # shape: (years, rows, cols)

    # Fit gamma parameters per pixel
    shape_arr = np.full(baseline_stack.shape[1:], np.nan, dtype=np.float32)
    scale_arr = np.full_like(shape_arr, np.nan)
    for r in range(baseline_stack.shape[1]):
        for c in range(baseline_stack.shape[2]):
            series = baseline_stack[:, r, c]
            if np.all(np.isnan(series)) or np.nanmean(series) <= 0:
                continue
            try:
                # Fit gamma distribution to positive precipitation values
                series_nonan = series[~np.isnan(series)]
                if len(series_nonan) >= 5:
                    fit_alpha, fit_loc, fit_beta = gamma.fit(series_nonan, floc=0)
                    shape_arr[r, c] = fit_alpha
                    scale_arr[r, c] = fit_beta
            except Exception:
                continue

    # Now calculate SPI for each year of this month
    for fname, year in by_month[month]:
        # Read precip array
        arr, gt, proj, nodata = read_raster_as_array(os.path.join(chirps_folder, fname))
        spi_arr = np.full_like(arr, np.nan)

        # Calculate SPI pixel by pixel
        for r in range(arr.shape[0]):
            for c in range(arr.shape[1]):
                if np.isnan(arr[r, c]) or np.isnan(shape_arr[r, c]):
                    continue
                try:
                    cdf = gamma.cdf(arr[r, c], shape_arr[r, c], scale=scale_arr[r, c])
                    # Convert to normal deviate (mean=0, std=1)
                    spi_arr[r, c] = norm.ppf(cdf)
                except Exception:
                    continue

        # Save output raster
        out_name = f"SPI1_{year:04d}_{month:02d}.tif"
        out_path = os.path.join(out_folder, out_name)
        save_array_as_raster(spi_arr, gt, proj, out_path, nodata)
        print("Saved:", out_path)

print("Done calculating SPI-1")
