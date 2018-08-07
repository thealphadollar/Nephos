from unittest import TestCase, mock

from nephos.uploader.uploader import Uploader, DBException


class Job:
    def __init__(self, id):
        self.id = id


@mock.patch('nephos.uploader.uploader.Uploader')
@mock.patch('nephos.uploader.uploader.LOG')
class TestUploader(TestCase):

    def test___init__(self, mock_log, mock_uploader):
        Uploader.__init__(mock_uploader, mock.ANY)

        self.assertTrue(mock_uploader.auth.called)
        self.assertTrue(mock_uploader.service is None)

    @mock.patch('nephos.uploader.uploader.DBHandler')
    def test_begin_uploads(self, mock_db, mock_log, _):
        Uploader.begin_uploads(mock_log)

        self.assertTrue(mock_db.connect.called)
        self.assertFalse(mock_log.warning.called)
        self.assertFalse(mock_log.debug.called)

    @mock.patch('nephos.uploader.uploader.DBHandler')
    def test_begin_uploads_fail(self, mock_db, mock_log, _):
        mock_db.connect.side_effect = DBException()
        Uploader.begin_uploads(mock_log)

        self.assertTrue(mock_db.connect.called)
        self.assertTrue(mock_log.warning.called)
        self.assertTrue(mock_log.debug.called)

    @mock.patch('nephos.uploader.uploader.DBHandler')
    def test_set_uploading(self, mock_db, mock_log, _):
        Uploader._set_uploading("test")

        self.assertTrue(mock_db.connect.called)
        self.assertFalse(mock_log.warning.called)

    @mock.patch('nephos.uploader.uploader.DBHandler')
    @mock.patch('nephos.uploader.uploader.shutil')
    def test_remove(self, mock_shutil, mock_db, mock_log, _):
        Uploader._remove("test")

        self.assertTrue(mock_db.connect.called)
        self.assertTrue(mock_shutil.rmtree.called)
        self.assertFalse(mock_log.warning.called)

    def test_add_to_scheduler(self, mock_log, mock_uploader):
        mock_uploader._config = {"timings": {"0": "01:00"}, "repetition": "1111111"}
        Uploader.add_to_scheduler(mock_uploader)

        self.assertTrue(mock_uploader._rm_old_jobs.called)
        self.assertTrue(mock_log.debug.called)
        self.assertTrue(mock_uploader._scheduler.add_cron_necessary_job.called)

    def test__rm_old_jobs(self, mock_log, mock_uploader):
        mock_uploader._scheduler.get_jobs.return_value = [Job("run_uploader@01:00")]
        Uploader._rm_old_jobs(mock_uploader)

        self.assertTrue(mock_uploader._scheduler.get_jobs.called)
        self.assertTrue(mock_uploader._scheduler.rm_recording_job.called)
        self.assertFalse(mock_log.warning.called)

    def test__get_name_file(self, _, __):
        expected = "test.tst"
        output = Uploader._get_name('/home/test/test.tst')

        self.assertEqual(expected, output)

    def test__get_name_folder(self, _, __):
        expected = "test"
        output = Uploader._get_name('/home/test')

        self.assertEqual(expected, output)