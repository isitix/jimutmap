import json


# The GeoRectangle class is used for creating a rectangle
# with the minimum and maximum latitude and longitude values from the given array of coordinates [[lon,lat ]...]
class GeoRectangle:
    def __init__(self, min_lon: float = None, max_lon: float = None, min_lat: float = None, max_lat: float = None):
        self.min_lon = min_lon
        self.max_lon = max_lon
        self.min_lat = min_lat
        self.max_lat = max_lat

    def setCoordinates(self, coordinates):
        self.min_lon = min(coordinates, key=lambda x: x[0])[0]
        self.max_lon = max(coordinates, key=lambda x: x[0])[0]
        self.min_lat = min(coordinates, key=lambda x: x[1])[1]
        self.max_lat = max(coordinates, key=lambda x: x[1])[1]

    def print(self):
        print(f'min_lon: {self.min_lon}, max_lon: {self.max_lon}, min_lat: {self.min_lat}, max_lat: {self.max_lat}')

    def __eq__(self, other):
        if isinstance(other, GeoRectangle):
            return (self.min_lon == other.min_lon and self.max_lon == other.max_lon
                    and self.min_lat == other.min_lat and self.max_lat == other.max_lat)
        return False

def parse_json_file(json_file_path):
    # parse json object
    poly_coordinates = []

    with open(json_file_path, 'r') as f:
        jsonObject = json.load(f)
    for feature in jsonObject['features']:
        if feature['geometry']['type'] == 'Polygon':
            coordinates = feature['geometry']['coordinates'][0]
            try:
                geo_rectangle = GeoRectangle()
                geo_rectangle.setCoordinates(coordinates)
                poly_coordinates.append(geo_rectangle)
            except ValueError as err:
                print(f'Error bad polygon format {err}')
    return poly_coordinates
