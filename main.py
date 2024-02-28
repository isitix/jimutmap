
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

file_path = 'geojson/SCT_rectangle.geojson'
geo_rectangle_list = parse_json_file(file_path)
filename = os.path.splitext(os.path.basename(file_path))[0]

for geo_rectangle in geo_rectangle_list:
    sanity_checker = SanityChecker(min_lat_deg=geo_rectangle.min_lat_deg,
                                   max_lat_deg=geo_rectangle.max_lat_deg,
                                   min_lon_deg=geo_rectangle.min_lon_deg,
                                   max_lon_deg=geo_rectangle.max_lon_deg,
                                   zoom=config.ZOOM,
                                   verbose=config.VERBOSE,
                                   threads_=config.THREADS_,
                                   container_dir=filename,
                                   v_number=config.V_NUMBER
                                           )
    sanity_checker.sanity_check()