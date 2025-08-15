import arcpy
import os
from arcpy.sa import ExtractByMask

# Enable Spatial Analyst extension
arcpy.CheckOutExtension("Spatial")

# Set workspace and output folder
input_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\NDVI_Data_2013FEB_2025JUL\NDVI_TIF"
output_folder = os.path.join(input_folder, "Clipped_NDVI")

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Set environment settings
arcpy.env.workspace = input_folder
arcpy.env.overwriteOutput = True

# Define the mask layer from the current project
mask_layer = "AOI_Provinces"

# Process each .tif file in the folder
for raster in arcpy.ListRasters("*.tif"):
    # Build output path
    out_name = f"clipped_{raster}"
    out_path = os.path.join(output_folder, out_name)

    # Perform Extract by Mask
    extracted = ExtractByMask(raster, mask_layer)

    # Save the output
    extracted.save(out_path)

    print(f"Extracted: {out_path}")

print("NDVI clipping completed.")