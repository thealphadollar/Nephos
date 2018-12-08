"""
Test Controller responsible for testing all the views in the /main folder
"""
from unittest import TestCase, mock
from tests.test_web.base import BaseTestCase

class test_Controllers(BaseTestCase):
    """
    Test Cases for the Main Views
    """
    def test_root(self):
        """
        Test the root
        """
        response = self.app.test_client().get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'Hello World!')

    def test_channels_view(self):
        """
        Test if Channel works properly
        """
        response = self.app.test_client().get('/channels')
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('channels.html')

    def test_channels_api(self):
        """
        Test if Channel works properly
        """
        response = self.app.test_client().get('/channels')
        self.assertEqual(response.status_code, 200)
        self.assertIn("bloomberg_europe", str(response.data))
        self.assertIn("EU", str(response.data))
        self.assertIn("239.255.20.19:1234", str(response.data))
        self.assertIn("spa", str(response.data))
        self.assertIn("up", str(response.data))
