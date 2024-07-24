import json


# The GeoRectangle class is used for creating a rectangle
# with the minimum and maximum latitude and longitude values from the given array of coordinates [[lon,lat ]...]
class MapArea:
    def __init__(self, min_lat: float = None, max_lat: float = None, min_lon: float = None, max_lon: float = None):
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lon = min_lon
        self.max_lon = max_lon

    def name(self):
        return f'{self.min_lat}-{self.min_lon}_{self.max_lat}-self.{self.max_lon}'
    def setCoordinates(self, coordinates):
        self.min_lon = min(coordinates, key=lambda x: x[0])[0]
        self.max_lon = max(coordinates, key=lambda x: x[0])[0]
        self.min_lat = min(coordinates, key=lambda x: x[1])[1]
        self.max_lat = max(coordinates, key=lambda x: x[1])[1]

    def print(self):
        print(f'min_lon: {self.min_lon}, max_lon: {self.max_lon}, min_lat: {self.min_lat}, max_lat: {self.max_lat}')

    def __eq__(self, other):
        if isinstance(other, WorldArea):
            return (self.min_lon == other.min_lon and self.max_lon == other.max_lon
                    and self.min_lat == other.min_lat and self.max_lat == other.max_lat)
        return False

def get_map_area_list(geojson_file):
    # parse json object
    map_area_list = []

    with open(geojson_file, 'r') as f:
        jsonObject = json.load(f)
    for feature in jsonObject['features']:
        if feature['geometry']['type'] == 'Polygon':
            coordinates = feature['geometry']['coordinates'][0]
            try:
                map_area = MapArea()
                map_area.setCoordinates(coordinates)
                map_area_list.append(map_area)
            except ValueError as err:
                print(f'Error bad polygon format {err}')
    return map_area_list
