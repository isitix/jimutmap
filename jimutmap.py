import ssl
import os
import math
import imghdr
import requests
import numpy as np
import datetime as dt
from typing import Tuple
from tqdm import tqdm
from os.path import join, exists, normpath, relpath
from typing import List

class ImageService:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0'
    }

    def __init__(self, access_key:str, min_lat_deg:float, max_lat_deg:float, min_lon_deg:float, max_lon_deg:float, zoom= 19, verbose:bool= False, threads_:int= 4, container_dir:str= "", get_mask:bool= False, v_number:int=0):
        """
        Zoom level. Between  1 and 20.

        Access key to Apple Maps. If not provided, will use a headless Chrome instance to fetch a session key.
        container_dir:str (default= "")
            When downloading images, place them in this directory.
            It will be created if it does not exist.
        """
        # Ignore SSL certificate errors
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE


        self.access_key = access_key
        self.set_bounds(min_lat_deg, max_lat_deg, min_lon_deg, max_lon_deg)
        self.zoom = zoom
        self.get_masks = get_mask
        self.output_dir = container_dir
        self.v_number = v_number

        if self.verbose:
            print(self.access_key,self.min_lat_deg,self.max_lat_deg,self.min_lon_deg,self.max_lon_deg,self.zoom,self.verbose,LOCKING_LIMIT)
        print("Initializing jimutmap ... Please wait...")


    @property
    def output_dir(self) -> str:
        """
        Get the output directory
        """
        return self._container_dir

    @output_dir.setter
    def output_dir(self, newDir:str):
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

    def latlon_to_xy(self, lat_deg:float, lon_deg:float) -> Tuple[int, int]:
        n = 2**self.zoom
        xTile = n * ((lon_deg + 180) / 360)
        lat_rad = lat_deg * math.pi / 180.0
        yTile = n * (1 - (math.log(math.tan(lat_rad) + 1/math.cos(lat_rad)) / math.pi)) / 2
        return int(xTile),int(yTile)

    def xy_to_latlon(self, xTile:int, yTile:int) -> Tuple[float, float]:
        n = 2**self.zoom
        lon_deg = int(xTile)/n * 360.0 - 180.0
#         lat_rad = math.atan(math.asinh(math.pi * (1 - 2 * int(yTile)/n)))
        lat_rad=2*((math.pi/4)-math.atan(math.exp(-1*math.pi*(1-2* int(yTile)/n))))
        lat_deg = lat_rad * 180.0 / math.pi
        return lat_deg, lon_deg

    def get_img(self, x, y):
        file_name = join(self.output_dir, f"{x}_{y}.jpg")


def get_img(self, x, y):
    filename = os.path.join(self.output_dir, f"{x}_{y}.jpg")
    if os.path.exists(filename):
        return

    req_url = self.get_req_img_url(x, y)
    r = requests.get(req_url, headers=ImageService.headers)
    content = r.content
    if not self.is_access_denied(content):
        with open(filename, 'wb') as fh:
            fh.write(r.content)
        if imghdr.what(filename) != 'jpeg':
            os.remove(filename)

    def get_req_img_url(self, xTile, yTile):
        req_url = f"https://sat-cdn1.apple-mapkit.com/tile?style=7&size=1&scale=1&z={self.zoom}&x={xTile}&y={yTile}&v={self.v_number}&accessKey={self.access_key}"
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
                URL_ALL.append(self.latlon_to_xy(i, j))
            if self.verbose:
                print("ALL URL CREATED! ...")

def test_KW(value):
    API = ImageService(value, 10, 80, 10, 80)
    print ('Test KW')
    print (API.access_key)
