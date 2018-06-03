from unittest import TestCase
from nephos.ver_info import VER_INFO


class TestVerInfo(TestCase):
    def test_print_VER_INFO(self):
        expected = "__title__ = 'Nephos'"
        self.assertIn(expected, VER_INFO)
