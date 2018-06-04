from unittest import TestCase, mock
from nephos.maintenance.main import Maintenance, _refresh_config


@mock.patch('nephos.maintenance.main.Maintenance')
class TestMaintenance(TestCase):

    @mock.patch('nephos.scheduler.Scheduler')
    def test_add_maintenance_to_scheduler(self, mock_scheduler, mock_maintenance):
        Maintenance.add_maintenance_to_scheduler(mock_maintenance, mock_scheduler)

        self.assertTrue(mock_scheduler.add_maintenance_jobs.called)

    @mock.patch('nephos.maintenance.main.DiskSpaceCheck')
    def test_call_disk_space_check(self, mock_disk_space, _):
        Maintenance.call_disk_space_check()

        call_args, _ = mock_disk_space.call_args
        self.assertIsInstance(call_args[0], dict)

    @mock.patch('nephos.maintenance.main.ChannelOnlineCheck')
    def test_call_channel_online_check(self, mock_channel_check, _):
        Maintenance.call_channel_online_check()

        call_args, _ = mock_channel_check.call_args
        self.assertIsInstance(call_args[0], dict)

    def test_call_uploader_auth_check(self, _):
        # TODO
        pass

    def test_call_file_upload_check(self, _):
        # TODO
        pass

    def test__get_maintenance_data(self, mock_maintenance):
        interval = 0
        mock_maintenance.config.__getitem__.side_effect = {
            'jobs': {
                'test': {
                    'interval': interval
                }
            }
        }.__getitem__
        return_interval = Maintenance._get_maintenance_data(mock_maintenance, 'test')

        self.assertEqual(return_interval, interval)

    @mock.patch('nephos.maintenance.main.Config')
    def test_refresh_config(self, mock_config, _):
        _refresh_config()

        self.assertTrue(mock_config.called)
