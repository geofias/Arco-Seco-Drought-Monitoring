import os
from datetime import datetime
from collections import defaultdict

# Folder where the renamed HDF files are located
folder_path = 'D:/GIS_Projects/DroughtMonitoring_ArcoSeco/NDVI_Data_2013FEB_2025JUL'

# Dictionary to store the best file per month (closest to the 15th)
monthly_images = {}

# Iterate through all files and group them by year-month
for filename in os.listdir(folder_path):
    if filename.endswith('.hdf') and filename.startswith('NDVI_'):
        try:
            # Extract date from filename
            date_str = filename.replace('NDVI_', '').replace('.hdf', '')
            date = datetime.strptime(date_str, '%Y_%m_%d')

            year_month = date.strftime('%Y-%m')

            # If this month is not stored yet, or this date is closer to the 15th, update it
            if year_month not in monthly_images:
                monthly_images[year_month] = (filename, abs(date.day - 15))
            else:
                current_closest = monthly_images[year_month][1]
                if abs(date.day - 15) < current_closest:
                    monthly_images[year_month] = (filename, abs(date.day - 15))

        except Exception as e:
            print(f"Skipping file {filename}: {e}")

# Create output folder if needed
output_folder = os.path.join(folder_path, 'monthly_selection')
os.makedirs(output_folder, exist_ok=True)

# Copy selected files to output folder
import shutil

for ym, (selected_file, _) in sorted(monthly_images.items()):
    src_path = os.path.join(folder_path, selected_file)
    dst_path = os.path.join(output_folder, selected_file)
    shutil.copy2(src_path, dst_path)
    print(f"Selected for {ym}: {selected_file}")