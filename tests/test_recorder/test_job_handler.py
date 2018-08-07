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
    @mock.patch('builtins.input')
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
    @mock.patch('builtins.input')
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
    @mock.patch('nephos.recorder.jobs.DBHandler')
    def test_load_jobs(self, mock_db, mock_log, mock_job_handler):
        JobHandler.load_jobs(mock_job_handler, MOCK_JOB_DATA)

        self.assertTrue(mock_db.connect.called)
        mock_job_handler.insert_jobs.assert_called_with(mock.ANY, mock.ANY)
        self.assertFalse(mock_log.warning.called)
        self.assertFalse(mock_log.debug.called)

    @mock.patch('nephos.recorder.jobs.LOG')
    @mock.patch('nephos.recorder.jobs.DBHandler')
    def test_load_jobs_error(self, mock_db, mock_log, mock_job_handler):
        mock_db.connect.side_effect = DBException
        JobHandler.load_jobs(mock_job_handler, MOCK_JOB_DATA)

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
            mock_job_handler.to_weekday.assert_called_with('0000000')
            self.assertTrue(mock_job_handler._scheduler.add_recording_job.called)

    def test_display_jobs(self, mock_job_handler):
        JobHandler.display_jobs(mock_job_handler)

        self.assertTrue(mock_job_handler._scheduler.get_jobs.called)

    def test_to_weekday(self, _):
        entry = '1111110'
        expected_output = 'mon,tue,wed,thu,fri,sat'
        output = JobHandler.to_weekday(entry)

        self.assertEqual(output, expected_output)
