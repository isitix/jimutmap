# ======================================================
# This tests the working of jimutmap package.
# Note this doesnot uses multi-processing 
# OPEN SOURCED UNDER GPL-V3.0.
# Author : Jimut Bahan Pal | jimutbahanpal@yahoo.com
# Project Website: https://github.com/Jimut123/jimutmap
# ======================================================

import os
from jimutmap import SanityChecker
import config
from geojson import parse_json_file

done_files = []

for element in os.listdir('plans'):
    file_path = os.path.join('plans', element)
    filename = os.path.splitext(os.path.basename(file_path))[0]
    if filename not in done_files:
        geo_rectangle_list = parse_json_file(file_path)
        print(f'Downloading images for {filename}')
        for geo_rectangle in geo_rectangle_list:
            geo_rectangle.print()
            try:
                sanity_checker = SanityChecker(min_lat_deg=geo_rectangle.min_lat,
                                                max_lat_deg=geo_rectangle.max_lat,
                                                min_lon_deg=geo_rectangle.min_lon,
                                                max_lon_deg=geo_rectangle.max_lon,
                                                zoom=config.ZOOM,
                                                verbose=config.VERBOSE,
                                                threads_=config.THREADS_,
                                                container_dir=os.path.join('satellite_images', filename),
                                                v_number=config.V_NUMBER
                                               )
                sanity_checker.sanity_check()
            except Exception as e:
                print(f'Bad georectangle skipping value, error {e}')
