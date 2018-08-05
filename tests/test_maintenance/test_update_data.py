from unittest import mock, TestCase

from nephos.maintenance.update_data import UpdateData, UpdateDataFailure


mock_config = {

}

mock_data = {
    "channels":
        {
            "test": "text"
        },
    "sharing_entity":
        {
            "test": "text"
        }
}


class MockUpdateData:
    @staticmethod
    def _get_data(_, __):
        return "text"


@mock.patch('nephos.maintenance.update_data.UpdateData')
class TestUpdateData(TestCase):

    @mock.patch('nephos.maintenance.update_data.super')
    @mock.patch('nephos.maintenance.update_data.Scheduler')
    @mock.patch('nephos.maintenance.update_data.JobHandler')
    @mock.patch('nephos.maintenance.update_data.Checker.__init__')
    def test_init(self, __, mock_job, mock_scheduler, _, mock_update_data):
        mock_update_data._get_data.return_value = "test"
        UpdateData.__init__(mock_update_data, mock_config)

        self.assertTrue(mock_scheduler.called)
        self.assertTrue(mock_job.called)

    @mock.patch('nephos.maintenance.update_data.add_to_report')
    @mock.patch('nephos.maintenance.update_data.LOG')
    def test_execute(self, mock_log, mock_report, mock_update_data):
        mock_update_data._compare.return_value = True, True
        UpdateData._execute(mock_update_data)

        self.assertTrue(mock_update_data._download_files.called)
        self.assertTrue(mock_update_data._compare.called)
        mock_update_data._update.assert_called_with("jobs")
        self.assertTrue(mock_update_data._remove_new_files.called)
        self.assertTrue(mock_report.called)
        self.assertTrue(mock_log.debug.called)
        self.assertTrue(mock_update_data._handle.called)

    @mock.patch('nephos.maintenance.update_data.add_to_report')
    @mock.patch('nephos.maintenance.update_data.LOG')
    def test_execute_fail(self, mock_log, mock_report, mock_update_data):
        mock_update_data._download_files.side_effect = UpdateDataFailure
        mock_update_data._compare.return_value = True, True
        UpdateData._execute(mock_update_data)

        self.assertTrue(mock_update_data._download_files.called)
        self.assertFalse(mock_update_data._compare.called)
        self.assertFalse(mock_update_data._update.called)
        self.assertFalse(mock_update_data._remove_new_files.called)
        self.assertFalse(mock_report.called)
        self.assertFalse(mock_log.debug.called)
        self.assertTrue(mock_update_data._handle.called)

    @mock.patch('nephos.maintenance.update_data.LOG')
    @mock.patch('urllib.request')
    def test__download_files(self, mock_request, mock_log, mock_update_data):
        UpdateData._download_files(mock_update_data)

        self.assertTrue(mock_request.urlretrieve.called)
        self.assertFalse(mock_log.debug.called)

    @mock.patch('nephos.maintenance.update_data.LOG')
    @mock.patch('urllib.request')
    def test__download_files_fail(self, mock_request, mock_log, mock_update_data):
        mock_request.urlretrieve.side_effect = Exception
        with self.failUnlessRaises(UpdateDataFailure):
            UpdateData._download_files(mock_update_data)

        self.assertTrue(mock_request.urlretrieve.called)
        self.assertTrue(mock_log.debug.called)

    @mock.patch('nephos.maintenance.update_data.cmp')
    def test__compare(self, mock_filecmp, _):
        UpdateData._compare()

        self.assertTrue(mock_filecmp.called)

    @mock.patch('nephos.maintenance.update_data.copy2')
    @mock.patch('nephos.maintenance.update_data.LOG')
    @mock.patch('nephos.maintenance.update_data.ChannelHandler')
    @mock.patch('nephos.maintenance.update_data.ShareHandler')
    @mock.patch('nephos.maintenance.update_data.Config')
    def test__update_channels(self, mock_config_handler, mock_shr_handler, mock_ch_handler, mock_log, mock_copy, mock_update_data):
        mock_config_handler.load_data.return_value = mock_data
        UpdateData._update(mock_update_data, "data")

        self.assertTrue(mock_config_handler.load_data.called)
        self.assertTrue(mock_ch_handler.delete_channel.called)
        self.assertTrue(mock_ch_handler.insert_channels.called)
        self.assertTrue(mock_shr_handler.delete_entity.called)
        self.assertTrue(mock_shr_handler.insert_share_entities.called)
        self.assertTrue(mock_copy.called)
        self.assertFalse(mock_log.warning.called)

    @mock.patch('nephos.maintenance.update_data.copy2')
    @mock.patch('nephos.maintenance.update_data.LOG')
    @mock.patch('nephos.maintenance.update_data.Config')
    def test__update_jobs(self, mock_config_handler, mock_log, mock_copy, mock_update_data):
        mock_config_handler.load_data.return_value = mock_data
        mock_update_data.job_handler.load_jobs.return_value = True
        UpdateData._update(mock_update_data, "jobs")

        self.assertTrue(mock_config_handler.load_data.called)
        self.assertTrue(mock_update_data.scheduler.start.called)
        self.assertTrue(mock_update_data.job_handler.rm_jobs.called)
        self.assertTrue(mock_update_data.job_handler.load_jobs.called)
        self.assertTrue(mock_copy.called)
        self.assertTrue(mock_update_data.scheduler.shutdown.called)
        self.assertFalse(mock_log.warning.called)

    @mock.patch('os.remove')
    def test__remove_new_files(self, mock_os, _):
        UpdateData._remove_new_files()

        self.assertTrue(mock_os.called)
