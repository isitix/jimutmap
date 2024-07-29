import math
import os
import requests
import aiohttp
import asyncio

import geojson
import sys
from typing import Tuple, List, Dict

requests.packages.urllib3.util.connection.HAS_IPV6 = False

def latlon_to_xy(lat_deg:float, lon_deg:float, zoom: int) -> Tuple[int, int]:
    n = 2**zoom
    xTile = n * ((lon_deg + 180) / 360)
    lat_rad = lat_deg * math.pi / 180.0
    yTile = n * (1 - (math.log(math.tan(lat_rad) + 1/math.cos(lat_rad)) / math.pi)) / 2
    return int(xTile),int(yTile)


def xy_to_latlon(x_tile:int, y_tile:int, zoom: int) -> Tuple[float, float]:
    n = 2**zoom
    lon_deg = int(x_tile) / n * 360.0 - 180.0
    lat_rad=2*((math.pi/4) - math.atan(math.exp(-1 * math.pi * (1 - 2 * int(y_tile) / n))))
    lat_deg = lat_rad * 180.0 / math.pi
    return lat_deg, lon_deg


async def download_file(session, url, filepath):
    async with session.get(url, verify_ssl=False) as response:
        if response.status == 429:
            raise Exception('Response status 429, rate limit exceeded')
        if response.status == 200:
            with open(filepath, 'wb') as file:
                file.write(await response.read())
            print(f"Downloaded {filepath}")


async def get_tiles(area, zoom, project_directory, api_key, limit=20):
    sem = asyncio.Semaphore(limit)

    async def bounded_download_file(session, url, filepath):
        async with sem:
            print(f"Downloading {url}")
            return await download_file(session, url, filepath)

    x1, y1 = latlon_to_xy(area.min_lat, area.min_lon, zoom)
    x2, y2 = latlon_to_xy(area.max_lat, area.max_lon, zoom)
    min_x = min(x1, x2)
    max_x = max(x1, x2)
    min_y = min(y1, y2)
    max_y = max(y1, y2)
    dir = os.path.join(project_directory, f"{zoom}_{area.name()}")
    if not os.path.exists(dir):
        os.makedirs(dir)
    tasks = []
    async with aiohttp.ClientSession() as session:
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                filename = f"{zoom}_{x}-{y}.jpg"
                filepath = os.path.join(dir, filename)
                if os.path.isfile(filepath) and os.path.getsize(filepath) > 0:
                    continue
                url = f"https://api.maptiler.com/tiles/satellite-v2/{zoom}/{x}/{y}.jpg?key={api_key}"
                print(f"Adding tile x={x}, y={y} to the queue")
                tasks.append(bounded_download_file(session, url, filepath))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    geojson_file = sys.argv[1]
    zoom = int(sys.argv[2])
    data_dir = sys.argv[3]
    api_key = sys.argv[4]
    area_list = geojson.get_map_area_list(geojson_file)
    project_name = os.path.basename(geojson_file)
    project_name = os.path.splitext(project_name)[0]
    project_directory = os.path.join(data_dir, project_name)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if not os.path.exists(project_directory):
        os.makedirs(project_directory)
    for area in area_list:
        asyncio.run(get_tiles(area, zoom, project_directory, api_key))
