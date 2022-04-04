# ======================================================
# This program downloads / scrapes Apple maps for free.
# OPEN SOURCED UNDER GPL-V3.0.
# Author : Jimut Bahan Pal | jimutbahanpal@yahoo.com
# Project Website: https://github.com/Jimut123/jimutmap
# pylint: disable = global-statement
# cSpell: words imghdr, tqdm, asinh, jimut, bahan
# ======================================================

import ssl
import os
import time
import math
import glob
import imghdr
import requests
import sqlite3
import numpy as np
import datetime as dt
from tqdm import tqdm
import multiprocessing
from jimutmap import api
from file_size import get_folder_size
from typing import Tuple
from selenium import webdriver
import chromedriver_autoinstaller
from multiprocessing.pool import ThreadPool
from os.path import join, exists, normpath, relpath



def generate_summary():
    # Create an approximate analysis of the space required
    total_files_downloaded = cur.execute(''' SELECT * FROM sanity ''')
    total_files_downloaded_val = cur.fetchall() #converts the cursor object to number
    total_number_of_files = len(total_files_downloaded_val)
    print("Total satellite images to be downloaded = ",total_number_of_files)
    print("Total roads tiles to be downloaded = ",total_number_of_files)
    disk_space = 10*2*total_number_of_files/1024
    print("Approx. estimated disk space required = {} MB".format(disk_space))


def create_sanity_db(min_lat, max_lat, min_lon, max_lon, latLonResolution):
    # To save all the expected file names to be downloaded
    for i in tqdm(np.arange(min_lat, max_lat, latLonResolution)):
        for j in np.arange(min_lon, max_lon, latLonResolution):
            xTile, yTile = sanity_obj.ret_xy_tiles(i,j)
            # print(xTile," ",yTile)
            # create the primary key for tracking values
            key_id = str(xTile)+"_"+str(yTile)
            # write the query
            query_insert = "INSERT OR IGNORE INTO sanity VALUES ('{}','{}','{}','{}','{}')".format(key_id,xTile, yTile, 0, 0)
            # Insert a row of records
            cur.execute(query_insert)


def update_sanity_db(folder_name):
    print("Updating sanity db ...")
    all_files_folder = glob.glob('{}/*'.format(folder_name))
    for tile_name in tqdm(all_files_folder):
        if tile_name.count('_') == 1:
            # then it is a satellite imagery
            xTile_val = str(tile_name.split('_')[0]).split('/')[-1]
            yTile_val = str(tile_name.split('_')[-1]).split('.')[0]
            create_id = str(xTile_val)+"_"+str(yTile_val)
            # print(create_id)
            cur.execute('''UPDATE sanity SET satellite_tile = 1 WHERE id = ?''',(str(create_id),))	# set the satellite_tile to 1

        if tile_name.count('_') == 2:
            # then it is a road mask 
            xTile_val = str(tile_name.split('_')[0]).split('/')[-1]
            yTile_val = str(tile_name.split('_')[-2])
            create_id = str(xTile_val)+"_"+str(yTile_val)
            # print(create_id)
            cur.execute('''UPDATE sanity SET road_tile = 1 WHERE id = ?''',(str(create_id),))	# set the road_tile to 1
    con.commit()



def shall_stop():
    # this function returns 1 if we need to stop, i.e., if all the entries are 1
    # which means all the required files are downloaded in the folder specified
    # even if one file is missing, we return 0
    
    # get all the number of 0 entries for satellite imagery
    get_sat_0s = cur.execute(''' SELECT * FROM sanity WHERE satellite_tile = 0 ''')
    get_sat_0s_val = cur.fetchall() #converts the cursor object to number
    total_number_of_sat0s = len(get_sat_0s_val)
    print("Total number of satellite images needed to be downloaded = ", total_number_of_sat0s)

    get_road_0s = cur.execute(''' SELECT * FROM sanity WHERE road_tile = 0 ''')
    get_road_0s_val = cur.fetchall() #converts the cursor object to number
    total_number_of_road0s = len(get_road_0s_val)
    print("Total number of satellite images needed to be downloaded = ", total_number_of_road0s)

    if total_number_of_sat0s == 0 and total_number_of_road0s == 0:
        return 1
    return 0


def check_downloading():
    # checks if the multiprocessing tool is still downloading the files or not
    # if there is a minute increase in byte size of the folder, we need to wait
    # till the multiprocessing thread finishes its execution
    get_folder_size_ini = get_folder_size('myOutputFolder')
    time.sleep(5)
    get_folder_size_final = get_folder_size('myOutputFolder')
    diff = get_folder_size_final - get_folder_size_ini
    if diff > 0:
        # we need to sleep for 5 seconds again
        return 1
    return 0


def get_sat_img_id():
    get_sat_0s = cur.execute(''' SELECT id FROM sanity WHERE satellite_tile = 0 ''')
    get_sat_0s_val = cur.fetchall() #converts the cursor object to number
    # print("Total number of satellite images needed to be downloaded = ", len(get_sat_0s_val))
    get_sat_ids = []
    for item in get_sat_0s_val:
        get_sat_ids.append(item[0])
    return get_sat_ids
    

def get_road_img_id():
    get_road_0s = cur.execute(''' SELECT * FROM sanity WHERE road_tile = 0 ''')
    get_road_0s_val = cur.fetchall() #converts the cursor object to number
    # print("Total number of satellite images needed to be downloaded = ", len(get_road_0s_val))
    get_road_ids = []
    for item in get_road_0s_val:
        get_road_ids.append(item[0])
    return get_road_ids




def sanity_check(threads_):
    # This function contains the main loop for checking the sanity of download
    # till all the files are downloaded


    # Create table sanity with the coordinates, and the corresponding
    # satellite tile and the road tile, id as the primary key xTile_yTile

    cur.execute('''CREATE TABLE IF NOT EXISTS sanity
                (id TEXT primary key, xTile INTEGER, yTile INTEGER, satellite_tile INTEGER, road_tile INTEGER )''')

    # check if the files are downloading or not, if so, then wait for certain seconds,
    # repeat this till the files stop downloading and then start the next batch of downloads

    batch = 1
    while(shall_stop() == 0):

        sat_img_ids = get_sat_img_id()
        road_img_ids = get_road_img_id()
        # print(sat_img_ids)
        # print(road_img_ids)

        if batch == 1:
            create_sanity_db(10,10.2,10,11,0.0005)  

        while(check_downloading()==1):
            print("Waiting for 5 seconds... Busy downloading")

        print("Batch ============================================================================= ",batch)
        print("===================================================================================")
        batch += 1

        # begin the operation here
        # url_str = [xtile, ytile]
        # TODO

         # To get the maximum number of threads
        MAX_CORES = multiprocessing.cpu_count()
        if threads_> MAX_CORES:
            print("Sorry, {} -- threads unavailable, using maximum CPU threads : {}".format(threads_,MAX_CORES))
            threads_ = MAX_CORES
        
        LOCKING_LIMIT = threads_

        tp=None
        URL_ALL = []
        print("Downloading all the satellite tiles: ")
        for sat_tile_name in sat_img_ids:
            xTile = sat_tile_name.split('_')[0]
            yTile = sat_tile_name.split('_')[0]
            URL_ALL.append([xTile, yTile])

            tp = ThreadPool(LOCKING_LIMIT)
            tp.imap_unordered(lambda x: sanity_obj.get_img(x, **kwargs), URL_ALL) #pylint: disable= unnecessary-lambda #cSpell:words imap
            tp.close()

        while(tp is not None):
            print("Waiting for thread to finish downloading satellite tiles")
            time.sleep(5)

        URL_ALL = []
        print("Downloading all the road tiles: ")
        for road_tile_name in road_img_ids:
            xTile = road_tile_name.split('_')[0]
            yTile = road_tile_name.split('_')[0]
            URL_ALL.append([xTile, yTile])

            tp = ThreadPool(LOCKING_LIMIT)
            tp.imap_unordered(lambda x: sanity_obj.get_img(x, **kwargs), URL_ALL) #pylint: disable= unnecessary-lambda #cSpell:words imap
            tp.close()

        while(tp is not None):
            rint("Waiting for thread to finish downloading road tiles")
            time.sleep(5)

        # continue the loop till there is no file left to download
        # generate the summary
        generate_summary()
        update_sanity_db('myOutputFolder')
        # Save (commit) the changes
        con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()


# connect to the temporary database that we shall use
con = sqlite3.connect('temp_sanity.sqlite')
cur = con.cursor()

# create the object of class jimutmap's api
sanity_obj = api(min_lat_deg = 10,
                    max_lat_deg = 10.2,
                    min_lon_deg = 10,
                    max_lon_deg = 10.2)

if __name__ == "__main__":
    # use main function for proper structuing of code
    sanity_check(threads_=50)