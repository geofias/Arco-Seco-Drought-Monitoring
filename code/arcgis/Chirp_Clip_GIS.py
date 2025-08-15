import arcpy
import os
from arcpy.sa import ExtractByMask

# Enable Spatial Analyst extension
arcpy.CheckOutExtension("Spatial")

# Input folder where original CHIRPS .tif files are located
input_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\Chirps"

# Temporary folder to store resampled rasters
resampled_folder = os.path.join(input_folder, "Resampled_250m")
if not os.path.exists(resampled_folder):
    os.makedirs(resampled_folder)

# Output folder for clipped rasters
clipped_folder = os.path.join(input_folder, "Clipped_250m")
if not os.path.exists(clipped_folder):
    os.makedirs(clipped_folder)

# Define environment
arcpy.env.workspace = input_folder
arcpy.env.overwriteOutput = True

# Define mask layer (already loaded in ArcGIS Pro project)
mask_layer = "AOI_Provinces"

# Define desired resolution (250 m in degrees ≈ 0.00225)
target_cell_size = "250"

# Optional: use NDVI raster to align pixels
snap_raster = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\NDVI_Data_2013FEB_2025JUL\NDVI_TIF\NDVI_2020_02_18.tif"
arcpy.env.snapRaster = snap_raster

# Loop over all .tif rasters
for raster in arcpy.ListRasters("*.tif"):
    print(f"Processing {raster}...")

    # Set paths
    resampled_path = os.path.join(resampled_folder, f"res_{raster}")
    clipped_path = os.path.join(clipped_folder, f"clip_{raster}")

    # Step 1: Resample to 250 m (approx.)
    arcpy.management.Resample(
        in_raster=raster,
        out_raster=resampled_path,
        cell_size=target_cell_size,
        resampling_type="BILINEAR"
    )

    # Step 2: Extract by Mask
    masked = ExtractByMask(resampled_path, mask_layer)
    masked.save(clipped_path)

    print(f"Saved: {clipped_path}")

print("All rasters processed successfully.")
