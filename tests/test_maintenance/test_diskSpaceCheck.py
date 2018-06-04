import os
from unittest import TestCase, mock
from nephos.maintenance.disk_space_check import DiskSpaceCheck

HOME = os.path.expanduser('~')


@mock.patch('nephos.maintenance.disk_space_check.DiskSpaceCheck')
class TestDiskSpaceCheck(TestCase):

    def test__execute_critical(self, mock_space_check):
        mock_space_check._get_data.return_value = 100
        mock_space_check._gb_to_bytes.return_value = 1024 ** 6
        mock_space_check._bytes_to_gbs.return_value = 100.0
        with mock.patch('nephos.maintenance.disk_space_check.__nephos_dir__', return_value=HOME):
            DiskSpaceCheck._execute(mock_space_check)

            mock_space_check._handle.assert_called_with(True, mock.ANY)

    def test__execute_not_critical(self, mock_space_check):
        mock_space_check._get_data.return_value = 0
        mock_space_check._gb_to_bytes.return_value = 0
        mock_space_check._bytes_to_gbs.return_value = 100.0
        with mock.patch('nephos.maintenance.disk_space_check.__nephos_dir__', return_value=HOME):
            DiskSpaceCheck._execute(mock_space_check)

            mock_space_check._handle.assert_called_with(False, mock.ANY)

    def test_conversion(self, _):
        in_bytes = 1024 * 1024 * 1024
        in_gb = 1

        return_gb = DiskSpaceCheck._bytes_to_gbs(in_bytes)
        self.assertEqual(return_gb, in_gb)

        return_bytes = DiskSpaceCheck._gb_to_bytes(in_gb)
        self.assertEqual(return_bytes, in_bytes)
