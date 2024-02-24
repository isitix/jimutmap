import json

# The GeoRectangle class is used for creating a rectangle
# with the minimum and maximum latitude and longitude values from the given array of coordinates [[lon,lat ]...]
class GeoRectangle:
    def __init__(self, coordinates):
        self.min_lon = min(coordinates, key=lambda x: x[0])[0]
        self.max_lon = max(coordinates, key=lambda x: x[0])[0]
        self.min_lat = min(coordinates, key=lambda x: x[1])[1]
        self.max_lat = max(coordinates, key=lambda x: x[1])[1]

    def print(self):
        print(f'min_lon: {self.min_lon}, max_lon: {self.max_lon}, min_lat: {self.min_lat}, max_lat: {self.max_lat}')

def parse_json_file(json_file_path):
    # parse json object
    poly_coordinates = []

    with open(json_file_path, 'r') as f:
        jsonObject = json.load(f)
    for feature in jsonObject['features']:
        if feature['geometry']['type'] == 'Polygon':
            coordinates = feature['geometry']['coordinates'][0]
            try:
                geo_rectangle = GeoRectangle(coordinates)
                poly_coordinates.append(geo_rectangle)
            except ValueError as err:
                print(f'Error bad polygon format {err}')
    return poly_coordinates


def main():
    parse_json_file('geojson/SCT_rectangle.geojson')[0].print()


if __name__ == "__main__":
    main()