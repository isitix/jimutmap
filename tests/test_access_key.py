import re
import unittest
from jimutmap import jimutmap


class TestGetAPIKey(unittest.TestCase):
    """
    Class for testing _get_api_key function in api class from jimutmap.py
    """

    def setUp(self):
        self.api_object = jimutmap.AccessKey(access_key='TEST')

    def test_none_access_key(self):
        self.api_object = jimutmap.AccessKey()
        self.assertGreater(len(self.api_object.access_key), 0)
    def test_renew_api_key_normal_condition(self):
        """
        Test _get_api_key function under normal condition
        """
        self.api_object.renew_access_key(my_access_key_id=self.api_object.get_access_key_id())
        self.assertIsInstance(self.api_object.access_key, str)
        self.assertGreater(len(self.api_object.access_key), 0)
        self.assertIsNotNone(re.match(r'[^\s&]+', self.api_object.access_key))
    def test_renew_api_key_timeout_error(self):
        """
        Test _get_api_key function when it raises a TimeoutError
        """
        with self.assertRaises(TimeoutError):
            self.api_object.renew_access_key(my_access_key_id=self.api_object.get_access_key_id(), timeout=0)

if __name__ == '__main__':
    unittest.main()
