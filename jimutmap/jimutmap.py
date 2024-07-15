import re
# ========================================================
# This program fetches tiles from satellites.pro for free.
# OPEN SOURCED UNDER GPL-V3.0.
# Author : Jimut Bahan Pal | jimutbahanpal@yahoo.com
# Project Website: https://github.com/Jimut123/jimutmap
# pylint: disable = global-statement
# cSpell: words imghdr, tqdm, asinh, jimut, bahan
# ========================================================

import ssl
import os
import time
import math
import imghdr
import requests
import numpy as np
import datetime as dt

from typing import Tuple
from tqdm import tqdm
from os.path import join, exists, normpath, relpath
from typing import List





# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0'
}



# To synchronize

LOCK_VAR = 0
UNLOCK_VAR = 0
LOCKING_LIMIT = 50 # MAX NO OF THREADS



class api:
    """
    Pull tiles from Apple Maps
    """
    def __init__(self, access_key:str, min_lat_deg:float, max_lat_deg:float, min_lon_deg:float, max_lon_deg:float, zoom= 19, verbose:bool= False, threads_:int= 4, container_dir:str= "", get_mask:bool= False, v_number:int=0):
        """
        Zoom level. Between  1 and 20.

        Access key to Apple Maps. If not provided, will use a headless Chrome instance to fetch a session key.
        container_dir:str (default= "")
            When downloading images, place them in this directory.
            It will be created if it does not exist.
        """
        global LOCKING_LIMIT
        # verbose is the first value to set because used elsewhere in the code
        self.verbose = bool(verbose)
        self.access_key = access_key
        self.set_bounds(min_lat_deg, max_lat_deg, min_lon_deg, max_lon_deg)
        self.zoom = zoom
        self.get_masks = get_mask
        self.container_dir = container_dir
        self.v_number = v_number

        MAX_CORES = 3
        if threads_> MAX_CORES:
            print("Sorry, {} -- threads unavailable, using maximum CPU threads : {}".format(threads_,MAX_CORES))
            threads_ = MAX_CORES
        
        LOCKING_LIMIT = threads_

        if self.verbose:
            print(self.access_key.access_key,self.min_lat_deg,self.max_lat_deg,self.min_lon_deg,self.max_lon_deg,self.zoom,self.verbose,LOCKING_LIMIT)
        print("Initializing jimutmap ... Please wait...")


    @property
    def container_dir(self) -> str:
        """
        Get the output directory
        """
        return self._container_dir

    @container_dir.setter
    def container_dir(self, newDir:str):
        try:
            if isinstance(newDir, str) and len(newDir) > 0:
                newDir = normpath(relpath(newDir))
                if not exists(newDir):
                    os.makedirs(newDir)
                    if self.verbose:
                        print(f"Creating target directory `{newDir}`")
                assert exists(newDir)
                self._container_dir = newDir
        except Exception: #pylint: disable= broad-except
            self._container_dir = ""


    def set_bounds(self, min_lat_deg:float, max_lat_deg:float, min_lon_deg:float, max_lon_deg:float):
        """
        Set the viewport bounds
        """
        assert -90 < min_lat_deg < 90
        assert -90 < max_lat_deg < 90
        assert min_lat_deg < max_lat_deg
        assert -180 < min_lon_deg < 180
        assert -180 < max_lon_deg < 180
        assert min_lon_deg < max_lon_deg
        # For compatibility with other funcs,
        # explicitly cast to float
        self.min_lat_deg = float(min_lat_deg)
        self.max_lat_deg = float(max_lat_deg)
        self.min_lon_deg = float(min_lon_deg)
        self.max_lon_deg = float(max_lon_deg)

    def _getLatBounds(self) -> Tuple[float, float]:
        """
        Internal getter for (min, max) latitude
        """
        return self.min_lat_deg, self.max_lat_deg

    def _getLonBounds(self) -> Tuple[float, float]:
        """
        Internal getter for (min, max) longitude
        """
        return self.min_lon_deg, self.max_lon_deg

    def ret_xy_tiles(self, lat_deg:float, lon_deg:float) -> Tuple[int, int]:
        """
        Parameters
        -----------------------

        lat_deg:float
        lon_deg:float

        Returns
        ----------------------
        tuple: (xTile, yTile)
        """
        n = 2**self.zoom
        xTile = n * ((lon_deg + 180) / 360)
        lat_rad = lat_deg * math.pi / 180.0
        yTile = n * (1 - (math.log(math.tan(lat_rad) + 1/math.cos(lat_rad)) / math.pi)) / 2
        return int(xTile),int(yTile)

    def ret_lat_lon(self, xTile:int, yTile:int) -> Tuple[float, float]:
        """
        Parameters
        -----------------------

        xTile:int
        yTile:int

        Returns
        ----------------------
        tuple: (lat, lng)
        """
        n = 2**self.zoom
        lon_deg = int(xTile)/n * 360.0 - 180.0
#         lat_rad = math.atan(math.asinh(math.pi * (1 - 2 * int(yTile)/n)))
        lat_rad=2*((math.pi/4)-math.atan(math.exp(-1*math.pi*(1-2* int(yTile)/n))))
        lat_deg = lat_rad * 180.0 / math.pi
        return lat_deg, lon_deg

    def make_url(self, lat_deg:float, lon_deg:float):
        """
        returns the list of urls when lat, lon, zoom and accessKey is provided

        Parameters
        -----------------------

        lat_deg:float
        lon_deg:float
        """
        xTile, yTile = self.ret_xy_tiles(lat_deg, lon_deg)
        return [xTile, yTile]

    def get_img(self, tile:List[str], prefix:str= "", retry:int= 3):
        """
        Get images from the URL provided and save them

        Parameters
        --------------------
        vNumber:int (default= 9042)
            The original version of this number was hardcoded as 7072,
            which was no longer working. Moved to a kwarg.

        retry:bool (default= False)
            Internal. Tracks retry status.
        """
        global headers, LOCK_VAR, UNLOCK_VAR, LOCKING_LIMIT
        my_api_key_id = 0
        if self.verbose:
            print(tile)
        UNLOCK_VAR = UNLOCK_VAR + 1
        LOCK_VAR = 1
        if self.verbose:
            print("UNLOCK VAR : ",UNLOCK_VAR)
        if UNLOCK_VAR >= LOCKING_LIMIT:
            LOCK_VAR = 0
            UNLOCK_VAR = 0
            if self.verbose:
                print("-------- UNLOCKING")
        xTile = tile[0]
        yTile = tile[1]
        file_name = join(self.container_dir, f"{prefix}{xTile}_{yTile}.jpg")
        attempt = 0
        while attempt < retry and not exists(file_name):
            attempt = attempt + 1
            try:
                req_url = self.get_req_img_url(xTile, yTile)
                if self.verbose:
                    print(f'Downloading file {file_name} attempt #{attempt}')
                r = requests.get(req_url, headers=headers)
                content = r.content
                if self.is_access_denied(content):
                    if self.verbose:
                        print('Access denied, refreshing api key')
                    my_api_key_id = self.access_key.renew_access_key(my_api_key_id)
                    continue
                with open(file_name, 'wb') as fh:
                    fh.write(r.content)
                if imghdr.what(file_name) != 'jpeg':
                    os.remove(file_name)
            except Exception as e:
                if self.verbose:
                    print(e)
        if self.get_masks:
            for cdn_level in range(1, 5):
                file_name_road = join(self.container_dir, f"{prefix}{xTile}_{yTile}_road{cdn_level}.png")
                attempt = 0
                while attempt < retry and not exists(file_name_road):
                    attempt = attempt + 1
                    today_date = str(dt.date.today())
                    year = today_date[0:4]
                    month = today_date[5:7]
                    day = today_date[8:10]
                    env_key = str(year)+str(month)+str(day)
                    req_url = self.get_req_road_url(cdn_level, env_key, xTile, yTile)
                    try:
                        r = requests.get(req_url, headers=headers)
                        if self.verbose:
                            print(f'Downloading file {file_name_road} attempt #{attempt}')
                        content = r.content
                        if self.is_access_denied(content):
                            self._get_api_key()
                            continue
                        with open(file_name_road, 'wb') as fh:
                            fh.write(r.content)
                        if imghdr.what(file_name_road) != 'png':
                            os.remove(file_name_road)
                            if self.verbose:
                                print(file_name_road,"NOT PNG")
                    except Exception as e:
                        if self.verbose:
                            print(e)

    def get_req_road_url(self, cdnLevel, env_key, xTile, yTile):
        # sample road tile 1: https://cdn3.apple-mapkit.com/ti/tile?country=IN&region=IN&style=46&size=1&x=390842&y=228268&z=19&scale=1&lang=en&v=2204054&poi=1&accessKey=1649243787_2102081627305478489_%2F_hIz9LjsZkMj6NE7y%2BimXS9vFQbxfjLBClZR7yqyFtsE%3D&emphasis=standard&tint=light
        # sample road tile 2: https://cdn4.apple-mapkit.com/ti/tile?country=IN&region=IN&style=46&size=1&x=296223&y=176608&z=19&scale=1&lang=en&v=2204054&poi=1&accessKey=1649243787_2102081627305478489_%2F_hIz9LjsZkMj6NE7y%2BimXS9vFQbxfjLBClZR7yqyFtsE%3D&emphasis=standard&tint=light
        req_url = f"https://cdn{cdnLevel}.apple-mapkit.com/ti/tile?country=US&region=US&style=46&size=1&x={xTile}&y={yTile}&z={self.zoom}&scale=1&lang=en&v={env_key}4&poi=1&accessKey={self.access_key.access_key}&emphasis=standard&tint=light"
        if self.verbose:
            print(req_url)
        return req_url

    def get_req_img_url(self, xTile, yTile):
        # sample sat tile: https://sat-cdn2.apple-mapkit.com/tile?style=7&size=1&scale=1&z=19&x=390843&y=228270&v=9262&accesskey=1649243787_2102081627305478489_%2f_hiz9ljszkmj6ne7y%2bimxs9vfqbxfjlbclzr7yqyftse%3d&emphasis=standard&tint=light
        req_url = f"https://sat-cdn1.apple-mapkit.com/tile?style=7&size=1&scale=1&z={self.zoom}&x={xTile}&y={yTile}&v={self.v_number}&accessKey={self.access_key.access_key}"
        if self.verbose:
            print(req_url)
        return req_url
    def is_access_denied(self, content):
        body = str(content).lower()
        return body.find("access denied") != -1

    def download(self, latLonResolution:float= 0.0005, **kwargs):
        """
        Downloads the tiles as initialized.

        Parameters
        --------------------------------

        getMasks:bool (default= False)
            Download the road PNG mask tile if true

        latLonResolution:float (default= 0.0005)
            The step size to use when creating tiles

        Also accepts kwargs for `get_img`.
        """
        min_lat, max_lat = self._getLatBounds()
        min_lon, max_lon = self._getLonBounds()
        if (max_lat - min_lat <= latLonResolution) or (max_lon - min_lon <= latLonResolution):
            # If we fail this check, then our arange will return no
            # results and we'll fetch nothing
            raise ValueError(f"Latitude and longitude bounds must be separated by at least the latLonResolution (currently {latLonResolution}). Either shrink the resolution value or increase the separation of your minimum/maximum latitude and longitude.")

        URL_ALL = []
        for i in tqdm(np.arange(min_lat, max_lat, latLonResolution)):
            tp = None
            for j in np.arange(min_lon, max_lon, latLonResolution):
                URL_ALL.append(self.make_url(i,j))
            if self.verbose:
                print("ALL URL CREATED! ...")
            global LOCK_VAR, UNLOCK_VAR, LOCKING_LIMIT
            if LOCK_VAR == 0:
                if self.verbose:
                    print("LOCKING")
                LOCK_VAR = 1
                UNLOCK_VAR = 0
                tp = ThreadPool(LOCKING_LIMIT)
                tp.imap_unordered(lambda x: self.get_img(x, **kwargs), URL_ALL) #pylint: disable= unnecessary-lambda #cSpell:words imap
                tp.close()
            # SEMAPHORE KINDA THINGIE
            if UNLOCK_VAR >= LOCKING_LIMIT and tp is not None:
                # If we have too many threads running, explicitly call
                # a wait on the threads until the most recent
                # process has cleared. As a practical matter, this will
                # clear _several_ threads and keep up performance
                tp.join()