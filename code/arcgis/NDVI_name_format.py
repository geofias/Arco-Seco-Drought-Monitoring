import os
from datetime import datetime, timedelta

# Path where your files are located
folder_path = 'D:/GIS_Projects/DroughtMonitoring_ArcoSeco/NDVI_Data_2013FEB_2025JUL'

for filename in os.listdir(folder_path):
    if filename.endswith('.hdf'):
        parts = filename.split('.')
        if len(parts) > 1 and parts[1].startswith('A'):
            julian_str = parts[1][1:]  # remove the 'A'
            year = int(julian_str[:4])
            day_of_year = int(julian_str[4:])

            # Convert Julian day to calendar date
            date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
            date_str = date.strftime('%Y_%m_%d')

            # Construct new filename
            new_filename = f'NDVI_{date_str}.hdf'
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)

            os.rename(old_path, new_path)
            print(f'Renamed: {filename} -> {new_filename}')