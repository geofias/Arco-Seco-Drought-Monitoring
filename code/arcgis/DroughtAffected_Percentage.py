import arcpy
import os
import re
import csv
from arcpy.sa import *

# ---------------- CONFIG ----------------
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# Folder with zscore rasters
z_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\NDVI_Data_2013FEB_2025JUL\NDVI_TIF\Clipped_NDVI_Real\NDVI_Anomalies"

# Zone layer (corregimientos)
zone_fc = "AOI_Corregimientos"
zone_id_field = "OBJECTID"         # Adjust
zone_name_field = "Corregimie"   # Adjust

# CSV outputs
csv_per_raster = os.path.join(z_folder, "z_exceed_by_raster_corregimiento.csv")
csv_summary = os.path.join(z_folder, "z_exceed_summary_by_corregimiento.csv")

# Thresholds
thr1 = 2.0
thr2 = 3.0

# ---------------- LOAD RASTERS ----------------
arcpy.env.workspace = z_folder
z_rasters = arcpy.ListRasters("zscore_*.tif") or []
if len(z_rasters) == 0:
    raise SystemExit("No zscore rasters found in folder: " + z_folder)

# Prepare CSV header for per-raster file
with open(csv_per_raster, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["raster_name", "date_yyyy_mm_dd", zone_id_field, zone_name_field,
                     "pixels_zone_total", f"pixels_abs_gt_{thr1}", f"pct_abs_gt_{thr1}",
                     f"pixels_abs_gt_{thr2}", f"pct_abs_gt_{thr2}"])

# Dictionary for cumulative stats
agg = {}

# Preload zone names
zone_names = {}
with arcpy.da.SearchCursor(zone_fc, [zone_id_field, zone_name_field]) as cur:
    for r in cur:
        zone_names[r[0]] = r[1]

# ---------------- MAIN LOOP ----------------
for zname in sorted(z_rasters):
    print("Processing:", zname)
    zpath = os.path.join(z_folder, zname)

    # Extract date from filename (pattern with YYYY_MM_DD)
    match = re.search(r"(\d{4}_\d{2}_\d{2})", zname)
    date_str = match.group(1) if match else ""

    zr = Raster(zpath)

    # Binary masks in memory
    bin_gt2 = Con(Abs(zr) > thr1, 1, 0)
    bin_gt3 = Con(Abs(zr) > thr2, 1, 0)

    # Count total pixels
    count_table = "in_memory\\count_table"
    ZonalStatisticsAsTable(zone_fc, zone_id_field, zr, count_table, "DATA", "MEAN")

    # Count exceedance pixels
    sum2_table = "in_memory\\sum2_table"
    sum3_table = "in_memory\\sum3_table"
    ZonalStatisticsAsTable(zone_fc, zone_id_field, bin_gt2, sum2_table, "DATA", "SUM")
    ZonalStatisticsAsTable(zone_fc, zone_id_field, bin_gt3, sum3_table, "DATA", "SUM")

    # Helper to read tables into dicts
    def table_to_dict(table_path, key_field, value_field):
        d = {}
        with arcpy.da.SearchCursor(table_path, [key_field, value_field]) as cursor:
            for row in cursor:
                d[row[0]] = row[1]
        return d

    counts = table_to_dict(count_table, zone_id_field, "COUNT")
    sum2 = table_to_dict(sum2_table, zone_id_field, "SUM")
    sum3 = table_to_dict(sum3_table, zone_id_field, "SUM")

    # Append per-zone results to CSV
    with open(csv_per_raster, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for zid, total_pix in counts.items():
            pix_gt2 = int(sum2.get(zid, 0) or 0)
            pix_gt3 = int(sum3.get(zid, 0) or 0)
            pct2 = (pix_gt2 / total_pix * 100.0) if total_pix and total_pix > 0 else 0.0
            pct3 = (pix_gt3 / total_pix * 100.0) if total_pix and total_pix > 0 else 0.0
            writer.writerow([zname, date_str, zid, zone_names.get(zid, ""), int(total_pix),
                             pix_gt2, round(pct2, 3), pix_gt3, round(pct3, 3)])

            # Update cumulative stats
            if zid not in agg:
                agg[zid] = {"name": zone_names.get(zid, ""), "total_pixels": 0,
                            "sum_gt2": 0, "sum_gt3": 0, "months_counted": 0}
            agg[zid]["total_pixels"] += int(total_pix)
            agg[zid]["sum_gt2"] += pix_gt2
            agg[zid]["sum_gt3"] += pix_gt3
            agg[zid]["months_counted"] += 1

# ---------------- SUMMARY CSV ----------------
with open(csv_summary, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([zone_id_field, zone_name_field, "months_counted",
                     "avg_pct_gt2_per_month", "avg_pct_gt3_per_month",
                     "pct_area_ever_gt2", "pct_area_ever_gt3"])
    for zid, info in agg.items():
        months = info["months_counted"]
        avg_pct2 = (info["sum_gt2"] / info["total_pixels"] * 100.0) / months if info["total_pixels"] > 0 else 0.0
        avg_pct3 = (info["sum_gt3"] / info["total_pixels"] * 100.0) / months if info["total_pixels"] > 0 else 0.0
        pct_ever2 = (info["sum_gt2"] / info["total_pixels"] * 100.0) if info["total_pixels"] > 0 else 0.0
        pct_ever3 = (info["sum_gt3"] / info["total_pixels"] * 100.0) if info["total_pixels"] > 0 else 0.0
        writer.writerow([zid, info["name"], months, round(avg_pct2, 3), round(avg_pct3, 3),
                         round(pct_ever2, 3), round(pct_ever3, 3)])

print("✅ Done")
print("Per-raster CSV:", csv_per_raster)
print("Summary CSV:", csv_summary)
