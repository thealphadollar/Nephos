from unittest import TestCase, mock
from nephos.recorder.jobs import JobHandler, DBException


MOCK_JOB_DATA = {
    0:
        {
            "name": "job_test",
            "channel_name": "ch_test",
            "start_time": "00:00",
            "duration": 0,
            "repetition": '0000000'
        }
}


@mock.patch('nephos.recorder.jobs.JobHandler')
class TestJobHandler(TestCase):

    @mock.patch('nephos.recorder.jobs.LOG')
    @mock.patch('nephos.recorder.jobs.input')
    @mock.patch('nephos.recorder.jobs.DBHandler')
    def test_add_job(self, mock_db, mock_input, mock_log, mock_job_handler):
        with mock.patch('nephos.recorder.jobs.validate_entries'):
            JobHandler.add_job(mock_job_handler)

        self.assertTrue(mock_input.called)
        self.assertTrue(mock_db.connect.called)
        mock_job_handler.insert_jobs.assert_called_with(mock.ANY, mock.ANY)
        self.assertFalse(mock_log.warning.called)
        self.assertFalse(mock_log.debug.called)

    @mock.patch('nephos.recorder.jobs.LOG')
    @mock.patch('nephos.recorder.jobs.input')
    @mock.patch('nephos.recorder.jobs.DBHandler')
    def test_add_job_error(self, mock_db, mock_input, mock_log, mock_job_handler):
        with mock.patch('nephos.recorder.jobs.validate_entries'):
            mock_db.connect.side_effect = DBException
            JobHandler.add_job(mock_job_handler)

        self.assertTrue(mock_input.called)
        self.assertTrue(mock_db.connect.called)
        self.assertFalse(mock_job_handler.insert_jobs.called)
        self.assertTrue(mock_log.warning.called)
        self.assertTrue(mock_log.debug.called)

    @mock.patch('nephos.recorder.jobs.LOG')
    @mock.patch('nephos.recorder.jobs.input', return_value='test')
    @mock.patch('nephos.recorder.jobs.Config')
    @mock.patch('nephos.recorder.jobs.DBHandler')
    def test_load_jobs(self, mock_db, mock_config, mock_input, mock_log, mock_job_handler):
        JobHandler.load_jobs(mock_job_handler)

        mock_input.assert_called_with("File path: ")
        mock_config.load_data.assert_called_with(mock.ANY, mock.ANY)
        self.assertTrue(mock_db.connect.called)
        mock_job_handler.insert_jobs.assert_called_with(mock.ANY, mock.ANY)
        self.assertFalse(mock_log.warning.called)
        self.assertFalse(mock_log.debug.called)

    @mock.patch('nephos.recorder.jobs.LOG')
    @mock.patch('nephos.recorder.jobs.input', return_value='test')
    @mock.patch('nephos.recorder.jobs.Config')
    @mock.patch('nephos.recorder.jobs.DBHandler')
    def test_load_jobs_error(self, mock_db, mock_config, mock_input, mock_log, mock_job_handler):
        mock_db.connect.side_effect = DBException
        JobHandler.load_jobs(mock_job_handler)

        mock_input.assert_called_with("File path: ")
        mock_config.load_data.assert_called_with(mock.ANY, mock.ANY)
        self.assertTrue(mock_db.connect.called)
        self.assertFalse(mock_job_handler.insert_jobs.called)
        self.assertTrue(mock_log.warning.called)
        self.assertTrue(mock_log.debug.called)

    @mock.patch('nephos.recorder.jobs.DBHandler')
    def test_insert_jobs(self, mock_db, mock_job_handler):
        with mock_db.connect() as db_cur, \
             mock.patch('os.path'):
            JobHandler.insert_jobs(mock_job_handler, db_cur, MOCK_JOB_DATA)

            db_cur.execute.assert_called_with(mock.ANY, mock.ANY)
            mock_job_handler._to_weekday.assert_called_with('0000000')
            self.assertTrue(mock_job_handler._scheduler.add_recording_job.called)

    def test_display_jobs(self, mock_job_handler):
        JobHandler.display_jobs(mock_job_handler)

        self.assertTrue(mock_job_handler._scheduler.get_jobs.called)

    @mock.patch('nephos.recorder.jobs.input')
    def test_rm_job(self, mock_input, mock_job_handler):
        JobHandler.rm_job(mock_job_handler)

        mock_input.assert_called_with("Job name: ")
        self.assertTrue(mock_job_handler._scheduler.rm_recording_job.called)

    def test__to_weekday(self, _):
        entry = '0100101'
        expected_output = 'tue fri sun'
        output = JobHandler._to_weekday(entry)

        self.assertEqual(output, expected_output)
