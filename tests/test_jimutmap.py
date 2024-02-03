import unittest
from jimutmap import jimutmap


class TestGetAPIKey(unittest.TestCase):
    """
    Class for testing _get_api_key function in api class from jimutmap.py
    """

    def setUp(self):
        self.api_object = jimutmap.api(min_lat_deg=0, max_lat_deg=10, min_lon_deg=20, max_lon_deg=30)

    def test_get_api_key_normal_condition(self):
        """
        Test _get_api_key function under normal condition
        """
        key = self.api_object._get_api_key()
        self.assertIsInstance(key, str)
        self.assertGreater(len(key), 0)

    def test_get_api_key_timeout_error(self):
        """
        Test _get_api_key function when it raises a TimeoutError
        """
        with self.assertRaises(TimeoutError):
            self.api_object._get_api_key(timeout = 0)


if __name__ == '__main__':
    unittest.main()
