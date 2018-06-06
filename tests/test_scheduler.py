from unittest import TestCase, mock
import os
import tempfile
from io import StringIO
from nephos.scheduler import Scheduler

TEMP_DIR = tempfile.TemporaryDirectory()
DB_JOBS_PATH = os.path.join(TEMP_DIR.name, "jobs.db")
MOCK_JOB_ID = 'xyz'


@mock.patch('nephos.scheduler.PATH_JOB_DB', DB_JOBS_PATH)
@mock.patch('nephos.scheduler.LOG')
class TestScheduler(TestCase):

    @mock.patch('nephos.scheduler.TMZ', new='utc')
    def test_init_utc(self, mock_log):
        Scheduler()
        mock_log.info.assert_called_with("Scheduler initialised with database at %s", DB_JOBS_PATH)
        mock_log.warning.assert_not_called()

    @mock.patch('nephos.scheduler.TMZ', new='IST')
    def test_init_ist(self, mock_log):
        Scheduler()
        mock_log.info.assert_called_with("Scheduler initialised with database at %s",
                                         DB_JOBS_PATH)
        mock_log.warning.assert_called_with("Unknown timezone %s, resetting timezone to 'utc'",
                                            'IST')

    def test_start_and_shutdown(self, mock_log):
        scheduler = Scheduler()
        scheduler.start()
        mock_log.info.assert_called_with("Scheduler running!")
        self.assertTrue(scheduler._scheduler.running)

        scheduler.shutdown()
        self.assertFalse(scheduler._scheduler.running)

    @mock.patch('nephos.scheduler.Scheduler')
    def test_add_recording_job(self, mock_scheduler, mock_log):
        Scheduler.add_recording_job(mock_scheduler, mock.ANY, mock.ANY, 0, '00:00',
                                    mock.ANY, mock.ANY)

        expected = 'Recording job added: %s'
        self.assertTrue(mock_scheduler._scheduler.add_job.called)
        self.assertIn(expected, mock_log.info.call_args[0])

    @mock.patch('nephos.scheduler.Scheduler')
    def test_add_maintenance_jobs(self, mock_scheduler, mock_log):
        Scheduler.add_maintenance_jobs(mock_scheduler, mock.ANY, mock.ANY, 0)

        expected = 'Maintenance job added: %s'
        self.assertTrue(mock_scheduler._scheduler.add_job.called)
        self.assertIn(expected, mock_log.debug.call_args[0])

    def test_get_jobs(self, _):
        output = Scheduler().get_jobs()

        self.assertIsInstance(output, list)

    @mock.patch('nephos.scheduler.Scheduler')
    def test_rm_recording_job(self, mock_scheduler, mock_log):
        Scheduler.rm_recording_job(mock_scheduler, MOCK_JOB_ID)

        mock_scheduler._scheduler.remove_job.assert_called_with(MOCK_JOB_ID)
        mock_log.info.assert_called_with("%s job removed from schedule", MOCK_JOB_ID)

    def test_rm_non_existing_recording_job(self, mock_log):
        Scheduler().rm_recording_job(MOCK_JOB_ID)

        self.assertTrue(mock_log.warning.called)
        self.assertTrue(mock_log.debug.called)
