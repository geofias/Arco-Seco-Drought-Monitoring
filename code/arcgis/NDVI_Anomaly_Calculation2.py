import arcpy
from arcpy.sa import *
import os
import re
import numpy as np
import csv

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# ----------------- CONFIG -----------------
input_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\NDVI_Data_2013FEB_2025JUL\NDVI_TIF\Clipped_NDVI_Real"
z_output_folder = os.path.join(input_folder, "NDVI_Anomalies")        # raw z-score (already created by your workflow)
vis_folder = os.path.join(input_folder, "NDVI_Anomalies_Vis")            # clipped-for-display rasters
summary_csv = os.path.join(input_folder, "NDVI_zscore_summary.csv")

os.makedirs(z_output_folder, exist_ok=True)
os.makedirs(vis_folder, exist_ok=True)

# Visualization clipping limits
min_vis = -5.0
max_vis = 5.0

# Thresholds for counts
threshold1 = 2.0
threshold2 = 3.0

# ---------- Helper: compute stats and produce clipped visualization ----------
def summarize_and_clip(z_raster_path, vis_out_path):
    """
    Given a z-score raster path, compute stats and save a clipped visualization raster.
    Returns a dict with summary stats.
    """
    # Load raster
    z_r = Raster(z_raster_path)

    # Convert raster to numpy array (preserves NoData as provided)
    arr = arcpy.RasterToNumPyArray(z_r, nodata_to_value=np.nan)

    # Mask invalid values (nan)
    valid_mask = ~np.isnan(arr)
    valid_vals = arr[valid_mask]

    # If no valid pixels, return None
    if valid_vals.size == 0:
        return None

    # Basic stats
    min_val = float(np.nanmin(valid_vals))
    max_val = float(np.nanmax(valid_vals))
    mean_val = float(np.nanmean(valid_vals))
    median_val = float(np.nanmedian(valid_vals))
    p5 = float(np.nanpercentile(valid_vals, 5))
    p95 = float(np.nanpercentile(valid_vals, 95))

    # Percent of valid pixels with |Z| > thresholds
    pct_gt_thr1 = 100.0 * np.sum(np.abs(valid_vals) > threshold1) / valid_vals.size
    pct_gt_thr2 = 100.0 * np.sum(np.abs(valid_vals) > threshold2) / valid_vals.size

    # Create visualization raster: clip to min_vis..max_vis for display
    # Use Con with Raster objects to preserve geotransform & metadata
    z_r_astype = z_r  # already Raster
    clipped = Con(z_r_astype < min_vis, min_vis, Con(z_r_astype > max_vis, max_vis, z_r_astype))

    # Save visualization raster
    clipped.save(vis_out_path)

    out = {
        "raster": os.path.basename(z_raster_path),
        "min": min_val,
        "max": max_val,
        "mean": mean_val,
        "median": median_val,
        "p5": p5,
        "p95": p95,
        f"pct_abs_gt_{threshold1}": pct_gt_thr1,
        f"pct_abs_gt_{threshold2}": pct_gt_thr2,
        "valid_pixels": int(valid_vals.size)
    }
    return out

# --------------- Main loop ---------------
pattern = re.compile(r"zscore_real_clipped_NDVI_\d{4}_\d{2}_\d{2}\.tif", re.IGNORECASE)

summaries = []

arcpy.env.workspace = z_output_folder
rasters = arcpy.ListRasters("zscore_*.tif") or []

if len(rasters) == 0:
    # Try fallback: search in input folder
    arcpy.env.workspace = input_folder
    rasters = arcpy.ListRasters("zscore_*.tif") or []

if len(rasters) == 0:
    raise Exception("No zscore rasters found. Check the filename pattern and folder paths.")

for rastname in rasters:
    z_path = os.path.join(arcpy.env.workspace, rastname)
    vis_name = f"vis_{rastname}"
    vis_out = os.path.join(vis_folder, vis_name)

    print(f"Processing summary & visualization for {rastname} ...")
    info = summarize_and_clip(z_path, vis_out)
    if info:
        summaries.append(info)
        print(f"  min {info['min']:.3f}  max {info['max']:.3f}  mean {info['mean']:.3f}  pct>|{threshold1}| {info[f'pct_abs_gt_{threshold1}']:.2f}%")
    else:
        print("  No valid pixels in raster; skipped.")

# Save summaries to CSV
if summaries:
    keys = list(summaries[0].keys())
    with open(summary_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, keys)
        writer.writeheader()
        for row in summaries:
            writer.writerow(row)
    print(f"\nSummary CSV saved to: {summary_csv}")
else:
    print("No summaries to write.")

print("\nDone.")