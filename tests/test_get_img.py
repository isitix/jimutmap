import unittest
from unittest.mock import patch, Mock
from os.path import exists, join
import requests
import sys
import imghdr
import os

sys.path.append('..')  # assuming the test file will be in a 'tests' sibling directory to 'jimutmap'
from jimutmap import api  # assuming jimutmap is the module name


class TestApiMethods(unittest.TestCase):
    def setUp(self):
        self.api = api(min_lat_deg=47.54, max_lat_deg=47.55, min_lon_deg=-2.92, max_lon_deg=-2.91, container_dir="portnavalo")

    @patch('os.remove')
    @patch('builtins.open')
    def test_get_img_access_denied(self, mock_open, mock_remove, mock_get):
        mock_get.return_value = Mock(content=b'access denied', text='access denied')
        with self.assertRaises(Exception):
            self.api.get_img([0, 0], vNumber=9651, getMask=False, prefix='')


    @patch('requests.get')
    @patch('os.remove')
    @patch('builtins.open')
    def test_get_img_not_jpeg(self, mock_open, mock_remove, mock_get):
        mock_get.return_value = Mock(content=b'non-jpeg-content', text='mock text')
        imghdr.what = Mock()
        imghdr.what.return_value = 'gif'
        self.api.get_img([0, 0], vNumber=9651, getMask=False, prefix='')
        imghdr.what.assert_called_with(join(self.api.container_dir, "00_00.jpg"))
        self.api.get_img([0, 0], vNumber=9651, getMask=False, prefix='')
        mock_remove.assert_called_with(join(self.api.container_dir, "00_00.jpg"))


if __name__ == "__main__":
    unittest.main()
