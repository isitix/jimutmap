
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

ACCESS_KEY = "1704837988_5451453327929905704_%2F_ow1SuEfsGeG0Y0JTulXXon3ru9qsKn1HjjSrFxxJGRo%3D"
CONTAINER_DIR = "british_fish_farms"
download_obj = api(min_lat_deg = 22.64,
                      max_lat_deg = 22.65,
                      min_lon_deg = 88.37,
                      max_lon_deg = 88.38,
                      zoom = 19,
                      verbose = False,
                      threads_ = 50, 
                      container_dir = CONTAINER_DIR,
                   ac_key=ACCESS_KEY)

# If you don't have Chrome and can't take advantage of the auto access key fetch, set
# here

# getMasks = False if you just need the tiles 
download_obj.download(getMasks = True)

# create the object of class jimutmap's api
sanity_obj = api(min_lat_deg = 22.64,
                      max_lat_deg = 22.65,
                      min_lon_deg = 88.37,
                      max_lon_deg = 88.38,
                      zoom = 19,
                      verbose = False,
                      threads_ = 50, 
                      container_dir = CONTAINER_DIR,
                   ac_key=ACCESS_KEY)

sanity_check(min_lat_deg = 22.64,
                max_lat_deg = 22.65,
                min_lon_deg = 88.37,
                max_lon_deg = 88.38,
                zoom = 19,
                verbose = False,
                threads_ = 50, 
                container_dir = CONTAINER_DIR
             )

print("Cleaning up... hold on")

sqlite_temp_files = glob.glob('*.sqlite*')



# update_stitcher_db("myOutputFolder")
# get_bbox_lat_lon()
stitch_whole_tile(save_name="Kolkata", folder_name="myOutputFolder")


print("Temporary sqlite files to be deleted = {} ? ".format(sqlite_temp_files))
inp = input("(y/N) : ")
if inp == 'y' or inp == 'yes' or inp == 'Y':
    for item in sqlite_temp_files:
        os.remove(item)



## Try to remove tree; if failed show an error using try...except on screen
try:
    chromdriver_folders = glob.glob('[0-9]*')
    print("Temporary chromedriver folders to be deleted = {} ? ".format(chromdriver_folders))
    inp = input("(y/N) : ")
    if inp == 'y' or inp == 'yes' or inp == 'Y':
        for item in chromdriver_folders:
            shutil.rmtree(item)
except OSError as e:
    print ("Error: %s - %s." % (e.filename, e.strerror))