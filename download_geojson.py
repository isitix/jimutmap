import os
import sys  # Added this line to get command line arguments
from jimutmap import SanityChecker
import config
from geojson import GeoRectangle
from geojson import parse_json_file

def main(geojson_file_path):
    coordinates = parse_json_file(geojson_file_path)
    for geo_rectangle in coordinates:

        min_lat = config.MIN_LAT_DEG
        while min_lat < config.MAX_LAT_DEG:
            container_dir = f'{config.CONTAINER_DIR}_{min_lat}_{min_lon}'
            sanity_checker = SanityChecker(min_lat_deg=min_lat,
                                           max_lat_deg=min_lat+config.STEP,
                                           min_lon_deg=min_lon,
                                           max_lon_deg=min_lon+config.STEP,
                                           zoom=config.ZOOM,
                                           verbose=config.VERBOSE,
                                           threads_=config.THREADS_,
                                           container_dir=container_dir,
                                           v_number=config.V_NUMBER
                                           )
            sanity_checker.sanity_check()
            # create an empty file to mark the dir as done
            with open(os.path.join(container_dir, 'done.txt'), 'w'):
                pass
            min_lat = min_lat + config.STEP
        min_lon = min_lon + config.STEP

if __name__ == '__main__':
    main(sys.argv[1])