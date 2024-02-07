
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

min_lat = config.MIN_LAT_DEG
min_lon = config.MIN_LON_DEG
step = config.STEP
while min_lon < config.MAX_LON_DEG:
    while min_lat < config.MAX_LAT_DEG:
        container_dir = f'{config.CONTAINER_DIR}_{min_lat}_{min_lon}'
        sanity_checker = SanityChecker(min_lat_deg=min_lat,
                                       max_lat_deg=min_lat+config.STEP,
                                       min_lon_deg=min_lon,
                                       max_lon_deg=min_lon+config.STEP,
                                       zoom=config.ZOOM,
                                       verbose=config.VERBOSE,
                                       threads_=config.THREADS_,
                                       container_dir=container_dir
                                       )
        sanity_checker.sanity_check()
        # create an empty file to mark the dir as done
        with open(os.path.join(container_dir, 'done.txt')):
            pass
        min_lon = min_lon + config.STEP
        min_lat = min_lat + config.STEP



