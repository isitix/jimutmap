# ======================================================
# This program checks the sanity of download.
# OPEN SOURCED UNDER GPL-V3.0.
# Author : Jimut Bahan Pal | jimutbahanpal@yahoo.com
# Project Website: https://github.com/Jimut123/jimutmap
# ======================================================

import time
import glob
import sqlite3
import numpy as np
from tqdm import tqdm
import multiprocessing
from jimutmap import api
from .file_size import get_folder_size
from multiprocessing.pool import ThreadPool


class SanityChecker:
    def __init__(self, min_lat_deg, max_lat_deg, min_lon_deg, max_lon_deg, zoom, verbose, threads_, container_dir, v_number):
        self.con = sqlite3.connect('temp_sanity.sqlite')
        self.cur = self.con.cursor()
        self.threads_ = threads_
        self.container_dir = container_dir
        # create the object of class jimutmap's api
        self.sanity_obj = api(min_lat_deg=min_lat_deg, max_lat_deg=max_lat_deg, min_lon_deg=min_lon_deg,
                              max_lon_deg=max_lon_deg, zoom=zoom, verbose=verbose,
                              threads_=self.threads_, container_dir=self.container_dir, v_number=v_number)
    def generate_summary(self):
        # Create an approximate analysis of the space required
        self.cur.execute(''' SELECT * FROM sanity ''')
        total_files_downloaded_val = self.cur.fetchall() #converts the cursor object to number
        total_number_of_files = len(total_files_downloaded_val)
        print("Total satellite images to be downloaded = ",total_number_of_files)
        print("Total roads tiles to be downloaded = ",total_number_of_files)
        disk_space = 10*2*total_number_of_files/1024
        print("Approx. estimated disk space required = {} MB".format(disk_space))

    def create_sanity_db(self, latLonResolution=0.0005):
        # To save all the expected file names to be downloaded
        for i in tqdm(np.arange(self.sanity_obj.min_lat_deg, self.sanity_obj.max_lat_deg, latLonResolution)):
            for j in np.arange(self.sanity_obj.min_lon_deg, self.sanity_obj.max_lon_deg, latLonResolution):
                xTile, yTile = self.sanity_obj.ret_xy_tiles(i,j)
                # print(xTile," ",yTile)
                # create the primary key for tracking values
                key_id = str(xTile)+"_"+str(yTile)
                # write the query
                query_insert = "INSERT OR IGNORE INTO sanity VALUES ('{}','{}','{}','{}','{}')".format(key_id,xTile, yTile, 0, 0)
                # Insert a row of records
                self.cur.execute(query_insert)
    def update_sanity_db(self, folder_name):
        # to take the files present in the folder and update all the entries of the
        # sanity database
        print("Updating sanity db ...")
        all_files_folder = glob.glob('{}/*'.format(folder_name))
        for tile_name in tqdm(all_files_folder):
            if tile_name.count('_') == 1:
                # then it is a satellite imagery
                xTile_val = str(tile_name.split('_')[0]).split('/')[-1]
                yTile_val = str(tile_name.split('_')[-1]).split('.')[0]
                create_id = str(xTile_val)+"_"+str(yTile_val)
                # print(create_id)
                self.cur.execute('''UPDATE sanity SET satellite_tile = 1 WHERE id = ?''',(str(create_id),))	# set the satellite_tile to 1

            if tile_name.count('_') == 2:
                # then it is a road mask
                xTile_val = str(tile_name.split('_')[0]).split('/')[-1]
                yTile_val = str(tile_name.split('_')[-2])
                create_id = str(xTile_val)+"_"+str(yTile_val)
                # print(create_id)
                self.cur.execute('''UPDATE sanity SET road_tile = 1 WHERE id = ?''',(str(create_id),))	# set the road_tile to 1
        self.con.commit()

    def shall_stop(self, get_masks):
        # this function returns 1 if we need to stop, i.e., if all the entries are 1
        # which means all the required files are downloaded in the folder specified
        # even if one file is missing, we return 0

        # get all the number of 0 entries for satellite imagery
        self.cur.execute(''' SELECT * FROM sanity WHERE satellite_tile = 0 ''')
        get_sat_0s_val = self.cur.fetchall() #converts the cursor object to number
        total_number_of_sat0s = len(get_sat_0s_val)
        print("Total number of satellite images needed to be downloaded = ", total_number_of_sat0s)
        if get_masks == True:
            self.cur.execute(''' SELECT * FROM sanity WHERE road_tile = 0 ''')
            get_road_0s_val = self.cur.fetchall() #converts the cursor object to number
            total_number_of_road0s = len(get_road_0s_val)
        else:
            total_number_of_road0s = 0
        print("Total number of satellite images needed to be downloaded = ", total_number_of_road0s)

        if total_number_of_sat0s == 0 and total_number_of_road0s == 0:
            return 1
        return 0
    def check_downloading(self):
        # checks if the multiprocessing tool is still downloading the files or not
        # if there is a minute increase in byte size of the folder, we need to wait
        # till the multiprocessing thread finishes its execution
        get_folder_size_ini = get_folder_size(self.sanity_obj.container_dir)
        time.sleep(15)
        get_folder_size_final = get_folder_size(self.sanity_obj.container_dir)
        diff = get_folder_size_final - get_folder_size_ini
        speed_download = diff/(15.0*1024*1024) # get the speed in MB
        if diff > 0:
            # we need to sleep for 5 seconds again
            print("Downloading speed == {} MiB/s ".format(speed_download))
            return 1
        return 0

    def get_sat_img_id(self):
        # to get all the satellite image ids which are not yet being downloaded
        self.cur.execute(''' SELECT id FROM sanity WHERE satellite_tile = 0 ''')
        get_sat_0s_val = self.cur.fetchall()  # converts the cursor object to number
        get_sat_ids = []
        for item in get_sat_0s_val:
            get_sat_ids.append(item[0])
        return get_sat_ids
    def get_road_img_id(self):
        # to get all the road  tiles image ids which are not yet being downloaded
        self.cur.execute(''' SELECT * FROM sanity WHERE road_tile = 0 ''')
        get_road_0s_val = self.cur.fetchall() #converts the cursor object to number
        get_road_ids = []
        for item in get_road_0s_val:
            get_road_ids.append(item[0])
        return get_road_ids
    def sanity_check(self, max_retry:int=1):
    # This function contains the main loop for checking the sanity of download
        # till all the files are downloaded

        # Create table sanity with the coordinates, and the corresponding
        # satellite tile and the road tile, id as the primary key xTile_yTile

        self.cur.execute('''CREATE TABLE IF NOT EXISTS sanity
                    (id TEXT primary key, xTile INTEGER, yTile INTEGER, satellite_tile INTEGER, road_tile INTEGER )''')

        # check if the files are downloading or not, if so, then wait for certain seconds,
        # repeat this till the files stop downloading and then start the next batch of downloads
        batch = 1
        self.create_sanity_db(latLonResolution=0.0005)
        self.generate_summary()
        retry = 0
        while(self.shall_stop(get_masks = self.sanity_obj.get_masks) == 0 and retry < max_retry):
            retry = retry + 1

            sat_img_ids = self.get_sat_img_id()

            while(self.check_downloading()==1):
                print("Waiting for 15 seconds... Busy downloading")

            print("Batch ============================================================================= ",batch)
            print("===================================================================================")
            batch += 1

            # begin the operation here
            # url_str = [xtile, ytile]
            # TODO

            # To get the maximum number of threads
            MAX_CORES = multiprocessing.cpu_count()
            if self.threads_> MAX_CORES:
                print("Sorry, {} -- threads unavailable, using maximum CPU threads : {}".format(self.threads_,MAX_CORES))
                self.threads_ = MAX_CORES

            LOCKING_LIMIT = self.threads_

            tp=None
            URL_ALL = []
            print("Downloading all the satellite tiles: ")
            for sat_tile_name in sat_img_ids:
                xTile = sat_tile_name.split('_')[0]
                yTile = sat_tile_name.split('_')[1]
                URL_ALL.append([xTile, yTile])

            # print(URL_ALL)
            tp = ThreadPool(LOCKING_LIMIT)
            tp.imap_unordered(lambda x: self.sanity_obj.get_img(x), URL_ALL) #pylint: disable= unnecessary-lambda #cSpell:words imap
            tp.close()

            self.update_sanity_db(self.sanity_obj.container_dir)
            self.con.commit()

            # continue the loop till there is no file left to download
            # generate the summary

        print("************************* Download Sucessful *************************")
        self.con.close()


