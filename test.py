
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
import access_key
import covered_zone

download_obj = api(min_lat_deg = covered_zone.MIN_LAT_DEG,
                      max_lat_deg = covered_zone.MAX_LAT_DEG,
                      min_lon_deg = covered_zone.MIN_LON_DEG,
                      max_lon_deg = covered_zone.MAX_LON_DEG,
                      zoom = covered_zone.ZOOM,
                      verbose = covered_zone.VERBOSE,
                      threads_ = covered_zone.THREADS_,
                      container_dir = covered_zone.CONTAINER_DIR,
                   ac_key=access_key.ACCESS_KEY)

# If you don't have Chrome and can't take advantage of the auto access key fetch, set
# here

# getMasks = False if you just need the tiles 
download_obj.download(getMasks = covered_zone.GET_MASKS)

# create the object of class jimutmap's api
sanity_obj = api(min_lat_deg = covered_zone.MIN_LAT_DEG,
                      max_lat_deg = covered_zone.MAX_LAT_DEG,
                      min_lon_deg = covered_zone.MIN_LON_DEG,
                      max_lon_deg = covered_zone.MAX_LON_DEG,
                      zoom = covered_zone.ZOOM,
                      verbose = covered_zone.VERBOSE,
                      threads_ = covered_zone.THREADS_,
                      container_dir = covered_zone.CONTAINER_DIR,
                   ac_key=access_key.ACCESS_KEY)

sanity_check(min_lat_deg = covered_zone.MIN_LAT_DEG,
                max_lat_deg = covered_zone.MAX_LAT_DEG,
                min_lon_deg = covered_zone.MIN_LON_DEG,
                max_lon_deg = covered_zone.MAX_LON_DEG,
                zoom = covered_zone.ZOOM,
                verbose = covered_zone.VERBOSE,
                threads_ = covered_zone.THREADS_,
                container_dir = covered_zone.CONTAINER_DIR
             )

print("Cleaning up... hold on")

sqlite_temp_files = glob.glob('*.sqlite*')
