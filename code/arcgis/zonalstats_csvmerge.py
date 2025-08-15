import arcpy
import os
import pandas as pd
import glob
import re

# ---------------- CONFIG ----------------
# Paths
zones_shp = "AOI_Corregimientos"
zone_field = "Corregimie"  # Change if your shapefile uses a different field name

ndvi_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\NDVI_Data_2013FEB_2025JUL\NDVI_TIF\Clipped_NDVI_Real\NDVI_Anomalies"
vci_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\NDVI_Data_2013FEB_2025JUL\NDVI_TIF\Clipped_NDVI_Real\NDVI_VCI"
spi_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\Chirps\Clipped_250m\SPI1"

out_tables_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\Zonal_Stats"
final_csv = os.path.join(out_tables_folder, "NDVI_VCI_SPI1_Merged.csv")
os.makedirs(out_tables_folder, exist_ok=True)

# Date range to process (YYYY, MM)
months_list = [(2023, m) for m in range(1, 13)] + \
              [(2024, m) for m in range(1, 13)] + \
              [(2025, m) for m in range(1, 7)]

# ---------------- FUNCTION: Find raster with flexible day ----------------
def find_raster(folder, pattern_base, year, month):
    """
    Search for raster file in 'folder' matching year and month, return full path.
    pattern_base should be something like 'zscore_real_clipped_NDVI' or 'VCI'.
    """
    search_pattern = os.path.join(folder, f"{pattern_base}_{year}_{month:02d}_*.tif")
    files = glob.glob(search_pattern)
    if not files:
        raise FileNotFoundError(f"No raster found for {pattern_base} {year}-{month:02d}")
    return files[0]  # If multiple, take the first match

# ---------------- FUNCTION: Zonal Stats ----------------
def run_zonal_stats(raster_path, out_table_path):
    arcpy.sa.ZonalStatisticsAsTable(
        in_zone_data=zones_shp,
        zone_field=zone_field,
        in_value_raster=raster_path,
        out_table=out_table_path,
        ignore_nodata="DATA",
        statistics_type="MEAN"
    )

# ---------------- RUN ZONAL STATS FOR EACH DATASET ----------------
ndvi_dfs = []
vci_dfs = []
spi_dfs = []

for year, month in months_list:
    # NDVI anomaly
    ndvi_file = find_raster(ndvi_folder, "zscore_real_clipped_NDVI", year, month)
    ndvi_table = os.path.join(out_tables_folder, f"NDVI_{year}_{month:02d}.dbf")
    run_zonal_stats(ndvi_file, ndvi_table)
    df_ndvi = pd.DataFrame(arcpy.da.TableToNumPyArray(ndvi_table, [zone_field, "MEAN"]))
    df_ndvi["Fecha"] = f"{year}-{month:02d}"
    df_ndvi.rename(columns={"MEAN": "NDVI_Anom"}, inplace=True)
    ndvi_dfs.append(df_ndvi)

    # VCI
    vci_file = find_raster(vci_folder, "VCI", year, month)
    vci_table = os.path.join(out_tables_folder, f"VCI_{year}_{month:02d}.dbf")
    run_zonal_stats(vci_file, vci_table)
    df_vci = pd.DataFrame(arcpy.da.TableToNumPyArray(vci_table, [zone_field, "MEAN"]))
    df_vci["Fecha"] = f"{year}-{month:02d}"
    df_vci.rename(columns={"MEAN": "VCI"}, inplace=True)
    vci_dfs.append(df_vci)

    # SPI-1 (no day in filename)
    spi_file = os.path.join(spi_folder, f"SPI1_{year}_{month:02d}.tif")
    if not os.path.exists(spi_file):
        raise FileNotFoundError(f"No SPI1 raster found for {year}-{month:02d}")
    spi_table = os.path.join(out_tables_folder, f"SPI1_{year}_{month:02d}.dbf")
    run_zonal_stats(spi_file, spi_table)
    df_spi = pd.DataFrame(arcpy.da.TableToNumPyArray(spi_table, [zone_field, "MEAN"]))
    df_spi["Fecha"] = f"{year}-{month:02d}"
    df_spi.rename(columns={"MEAN": "SPI_1"}, inplace=True)
    spi_dfs.append(df_spi)

# ---------------- MERGE ALL ----------------
df_ndvi_all = pd.concat(ndvi_dfs, ignore_index=True)
df_vci_all = pd.concat(vci_dfs, ignore_index=True)
df_spi_all = pd.concat(spi_dfs, ignore_index=True)

merged = pd.merge(df_ndvi_all, df_vci_all, on=[zone_field, "Fecha"])
merged = pd.merge(merged, df_spi_all, on=[zone_field, "Fecha"])

# Save final CSV
merged.to_csv(final_csv, index=False, encoding="utf-8-sig")
print(f"Final table saved at: {final_csv}")
