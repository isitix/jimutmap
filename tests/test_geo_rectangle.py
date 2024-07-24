import unittest
from geojson import WorldArea


class TestGeoRectangle(unittest.TestCase):
    def test_initial_coordinates(self):
        rect = WorldArea(3.3, 4.4, 1.1, 2.2)
        self.assertEqual(rect.min_lon, 1.1)
        self.assertEqual(rect.max_lon, 2.2)
        self.assertEqual(rect.min_lat, 3.3)
        self.assertEqual(rect.max_lat, 4.4)

    def test_set_coordinates(self):
        rect = WorldArea()
        coordinates = [(10, 20), (30, 40), (40, 60), (50, 80)]
        rect.setCoordinates(coordinates)

        self.assertEqual(rect.min_lon, 10)
        self.assertEqual(rect.max_lon, 50)
        self.assertEqual(rect.min_lat, 20)
        self.assertEqual(rect.max_lat, 80)

    def test_equal(self):
        rect1 = WorldArea(3.3, 4.4, 1.1, 2.2)
        rect2 = WorldArea(3.3, 4.4, 1.1, 2.2)
        self.assertTrue(rect1 == rect2)

    def test_not_equal(self):
        rect1 = WorldArea(3.4, 4.5, 1.2, 2.3)
        rect2 = WorldArea(3.3, 4.4, 1.1, 2.2)
        self.assertFalse(rect1 == rect2)


if __name__ == '__main__':
    unittest.main()
