
# ======================================================
# This tests the working of jimutmap package.
# Note this doesnot uses multi-processing 
# OPEN SOURCED UNDER GPL-V3.0.
# Author : Jimut Bahan Pal | jimutbahanpal@yahoo.com
# Project Website: https://github.com/Jimut123/jimutmap
# ======================================================

# Using map tiles for Kolkata, Baranagar my hometown: 22.645899,88.373889,19
import os
import glob
import shutil
from jimutmap import api, sanity_check, stitch_whole_tile
import config

download_obj = api(min_lat_deg = config.MIN_LAT_DEG,
                      max_lat_deg = config.MAX_LAT_DEG,
                      min_lon_deg = config.MIN_LON_DEG,
                      max_lon_deg = config.MAX_LON_DEG,
                      zoom = config.ZOOM,
                      verbose = config.VERBOSE,
                      threads_ = config.THREADS_,
                      container_dir = config.CONTAINER_DIR,
                   ac_key = config.ACCESS_KEY)

# create the object of class jimutmap's api
sanity_check(min_lat_deg = config.MIN_LAT_DEG,
                max_lat_deg = config.MAX_LAT_DEG,
                min_lon_deg = config.MIN_LON_DEG,
                max_lon_deg = config.MAX_LON_DEG,
                zoom = config.ZOOM,
                verbose = config.VERBOSE,
                threads_ = config.THREADS_,
                container_dir = config.CONTAINER_DIR
             )

print("Cleaning up... hold on")

sqlite_temp_files = glob.glob('*.sqlite*')
