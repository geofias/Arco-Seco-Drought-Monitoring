import arcpy
import os
from arcpy.sa import Raster

arcpy.CheckOutExtension("Spatial")

# Folder with clipped NDVI rasters (Int16)
input_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\NDVI_Data_2013FEB_2025JUL\NDVI_TIF\Clipped_NDVI"
output_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\NDVI_Data_2013FEB_2025JUL\NDVI_TIF\Clipped_NDVI_Real"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

arcpy.env.workspace = input_folder
arcpy.env.overwriteOutput = True

for raster in arcpy.ListRasters("*.tif"):
    print(f"Converting {raster}...")

    in_raster = Raster(raster)
    real_ndvi = in_raster / 10000.0

    out_path = os.path.join(output_folder, f"real_{raster}")
    real_ndvi.save(out_path)

    print(f"Saved: {out_path}")

print("NDVI conversion completed.")