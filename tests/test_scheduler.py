from unittest import TestCase, mock
import os
import tempfile
from io import StringIO
from nephos.scheduler import Scheduler

temp_dir = tempfile.TemporaryDirectory()
DB_JOBS_PATH = os.path.join(temp_dir.name, "jobs.db")
mock_job_id = 'xyz'


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
        mock_log.info.assert_called_with("Scheduler initialised with database at %s", DB_JOBS_PATH)
        mock_log.warning.assert_called_with("Unknown timezone %s, resetting timezone to 'utc'", 'IST')
        mock_log.error.assert_called_with(mock.ANY)

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
        self.assertIn(expected, mock_log.info.call_args[0])

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_print_jobs(self, mock_output, _):
        Scheduler().print_jobs()
        output = mock_output.getvalue()
        expected = "Pending jobs:"
        self.assertIn(expected, output)

    @mock.patch('nephos.scheduler.Scheduler')
    def test_rm_recording_job(self, mock_scheduler, mock_log):
        with mock.patch('nephos.scheduler.input', return_value=mock_job_id):
            Scheduler.rm_recording_job(mock_scheduler)
            mock_scheduler._scheduler.remove_job.assert_called_with(mock_job_id)
            mock_log.info.assert_called_with("%s job removed from schedule", mock_job_id)

    def test_rm_non_existing_recording_job(self, mock_log):
        with mock.patch('nephos.scheduler.input', return_value=mock_job_id):
            Scheduler().rm_recording_job()
            self.assertTrue(mock_log.error.called)
