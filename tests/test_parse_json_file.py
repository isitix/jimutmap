import unittest
from pathlib import Path
from geojson import parse_json_file
from geojson import PlanetArea
import json


class TestGeoJson(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_json_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [30, 12],
                            [40.3, 40],
                            [20, 50.5],
                            [10, 20],
                            [30, 1]
                        ]]
                    }
                }
            ]
        }
        cls.test_geo_rectangle = PlanetArea(1, 50.5, 10, 40.3)

    def test_parse_sample_json_file(self):
        temp_filename = "/tmp/sample.json"
        with open(temp_filename, "w") as f:
            json.dump(self.test_json_data, f)

        result = parse_json_file(temp_filename)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.test_geo_rectangle)

    def test_empty_json(self):
        with open("/tmp/empty.json", "w") as f:
            json.dump({"type": "FeatureCollection", "features": []}, f)

        result = parse_json_file("/tmp/empty.json")
        self.assertEqual(len(result), 0)

    def test_invalid_json(self):
        with open("/tmp/invalid.json", "w") as f:
            f.write("{malformed json")

        with self.assertRaises(json.JSONDecodeError):
            _ = parse_json_file("/tmp/invalid.json")

    def test_non_existent_file(self):
        non_existent_file = "/tmp/non_existent.json"
        if Path(non_existent_file).is_file():
            Path(non_existent_file).unlink()
        with self.assertRaises(FileNotFoundError):
            _ = parse_json_file(non_existent_file)

    def test_non_polygon_json(self):
        non_polygon_data = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "NonPolygon",
                    "coordinates": [[
                        [30, 10], [40, 40], [20, 40], [10, 20], [30, 10]
                    ]]
                }
            }]
        }

        with open("/tmp/non_polygon.json", "w") as f:
            json.dump(non_polygon_data, f)

        result = parse_json_file("/tmp/non_polygon.json")
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    unittest.main()
