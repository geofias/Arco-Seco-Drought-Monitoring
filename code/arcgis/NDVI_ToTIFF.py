import os
from osgeo import gdal

input_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\NDVI_Data_2013FEB_2025JUL\monthly_selection"
output_folder = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\NDVI_Data_2013FEB_2025JUL\NDVI_TIF"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith(".hdf"):
        hdf_path = os.path.join(input_folder, filename)

        # Open HDF file
        hdf_dataset = gdal.Open(hdf_path)

        # List subdatasets (you'll need to pick the correct one, usually NDVI is first)
        subdatasets = hdf_dataset.GetSubDatasets()
        ndvi_subdataset = subdatasets[0][0]  # 0 is usually NDVI for MOD13Q1

        # Create output path with .tif
        output_tif = os.path.join(output_folder, filename.replace(".hdf", ".tif"))

        # Translate to GeoTIFF
        gdal.Translate(output_tif, ndvi_subdataset)

        print(f"Converted {filename} to {output_tif}")
