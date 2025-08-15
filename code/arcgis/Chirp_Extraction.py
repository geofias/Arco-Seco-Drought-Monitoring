import os
import gzip
import shutil

# Paths
input_dir = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\Chirps"
output_dir = r"D:\GIS_Projects\DroughtMonitoring_ArcoSeco\Chirps\Chirps_Extracted"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Loop through all .gz files in input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".gz"):
        gz_path = os.path.join(input_dir, filename)

        # Extract base name for output .tif file
        tif_filename = filename[:-3]  # remove .gz extension
        tif_path = os.path.join(output_dir, tif_filename)

        # Extract .tif from .gz
        with gzip.open(gz_path, 'rb') as f_in:
            with open(tif_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

print("Extraction complete. All .tif files saved to:", output_dir)