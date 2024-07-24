import math
import os
import requests
import geojson
import sys

def latlon_to_xy(self, lat_deg:float, lon_deg:float, zoom: int) -> Tuple[int, int]:
    n = 2**zoom
    xTile = n * ((lon_deg + 180) / 360)
    lat_rad = lat_deg * math.pi / 180.0
    yTile = n * (1 - (math.log(math.tan(lat_rad) + 1/math.cos(lat_rad)) / math.pi)) / 2
    return int(xTile),int(yTile)

def xy_to_latlon(self, xTile:int, yTile:int, zoom) -> Tuple[float, float]:
    n = 2**zoom
    lon_deg = int(xTile)/n * 360.0 - 180.0
    #         lat_rad = math.atan(math.asinh(math.pi * (1 - 2 * int(yTile)/n)))
    lat_rad=2*((math.pi/4)-math.atan(math.exp(-1*math.pi*(1-2* int(yTile)/n))))
    lat_deg = lat_rad * 180.0 / math.pi
    return lat_deg, lon_deg

def get_tiles(area, zoom, project_directory, api_key):
    xmin, ymin = latlon_to_xy(area.minlat, area.minlon, zoom)
    xmax, ymax = latlon_to_xy(area.maxlat, area.maxlon, zoom)
    dir = f"{zoom}_{area.name()}"
    if not os.path.exists(dir):
        os.makedirs(dir)
    for x in range(xmin, xmax):
        for y in range(ymin, ymax):
            filename = f"{zoom}_{x}-{y}.geojson"
            filepath = os.path.join(dir, filename)
            if os.path.isfile(filepath) and os.path.getsize(filepath) > 0:
                break
            url = f"https://api.maptiler.com/tiles/satellite-v2/{zoom}/{x}/{y}.jpg?key={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                with open(filepath, 'wb') as file:
                    file.write(response.content)

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
        get_tiles(area, zoom, project_directory, api_key)
