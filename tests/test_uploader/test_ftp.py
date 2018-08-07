from unittest import TestCase, mock
import ftplib

from nephos.uploader.ftp import FTPUploader, FTPFailure


@mock.patch('nephos.uploader.ftp.FTPUploader')
@mock.patch('nephos.uploader.ftp.LOG')
class TestFTPUploader(TestCase):

    @mock.patch('nephos.uploader.ftp.ftplib')
    @mock.patch('nephos.uploader.ftp.add_to_report')
    def test___init__(self, mock_report, mock_ftp_lib, mock_log, mock_ftp):
        mock_ftp._get_ftp_config.return_value = "test", "test", "test", "test"
        tasks_list = ["test task"]
        FTPUploader.__init__(mock_ftp, tasks_list)

        self.assertTrue(mock_ftp._get_ftp_config.called)
        self.assertTrue(mock_ftp_lib.FTP.called)
        self.assertTrue(mock_ftp._auth.called)
        self.assertTrue(mock_ftp._create_folder.called)
        self.assertTrue(mock_ftp.ftp.cwd.called)
        self.assertTrue(mock_ftp._upload.called)
        self.assertTrue(mock_report.called)
        self.assertFalse(mock_log.warning.called)

    @mock.patch('nephos.uploader.ftp.ftplib')
    @mock.patch('nephos.uploader.ftp.add_to_report')
    def test___init___empty_config(self, mock_report, mock_ftp_lib, mock_log, mock_ftp):
        mock_ftp._get_ftp_config.return_value = None, "test", "test", "test"
        tasks_list = ["test task"]
        FTPUploader.__init__(mock_ftp, tasks_list)

        self.assertTrue(mock_ftp._get_ftp_config.called)
        self.assertFalse(mock_ftp_lib.FTP.called)
        self.assertFalse(mock_ftp._auth.called)
        self.assertFalse(mock_ftp._create_folder.called)
        self.assertFalse(mock_ftp.ftp.cwd.called)
        self.assertFalse(mock_ftp._upload.called)
        self.assertTrue(mock_report.called)
        self.assertTrue(mock_log.warning.called)

    @mock.patch('nephos.uploader.ftp.os')
    def test__upload(self, mock_os, _, mock_ftp):
        mock_os.path.join.return_value = "test"
        FTPUploader._upload(mock_ftp, "test_dir")

        self.assertTrue(mock_ftp._get_name.called)
        self.assertTrue(mock_os.listdir.called)
        self.assertTrue(mock_os.path.join.called)
        self.assertTrue(mock_ftp._get_name.called)

    @mock.patch('nephos.uploader.ftp.add_to_report')
    def test__auth(self, mock_report, mock_log, mock_ftp):
        FTPUploader._auth(mock_ftp, "test", "test", "test", "test")

        self.assertTrue(mock_ftp.ftp.connect.called)
        self.assertFalse(mock_report.called)
        self.assertFalse(mock_log.error.called)
        self.assertTrue(mock_ftp.ftp.login.called)
        self.assertTrue(mock_log.debug.called)

    @mock.patch('nephos.uploader.ftp.add_to_report')
    def test__auth_fail_connection(self, mock_report, mock_log, mock_ftp):
        mock_ftp.ftp.connect.side_effect = ConnectionError()
        with self.failUnlessRaises(FTPFailure):
            FTPUploader._auth(mock_ftp, "test", "test", "test", "test")

        self.assertTrue(mock_ftp.ftp.connect.called)
        self.assertTrue(mock_report.called)
        self.assertTrue(mock_log.error.called)
        self.assertFalse(mock_ftp.ftp.login.called)
        self.assertTrue(mock_log.debug.called)

    @mock.patch('nephos.uploader.ftp.add_to_report')
    def test__auth_fail_login(self, mock_report, mock_log, mock_ftp):
        mock_ftp.ftp.login.side_effect = ftplib.error_perm()
        with self.failUnlessRaises(FTPFailure):
            FTPUploader._auth(mock_ftp, "test", "test", "test", "test")

        self.assertTrue(mock_ftp.ftp.connect.called)
        self.assertTrue(mock_report.called)
        self.assertTrue(mock_log.error.called)
        self.assertTrue(mock_ftp.ftp.login.called)
        self.assertTrue(mock_log.debug.called)

    def test__create_folder(self, mock_log, mock_ftp):
        expected = "/test"
        output = FTPUploader._create_folder(mock_ftp, "test")

        self.assertEqual(expected, output)
        self.assertTrue(mock_ftp.ftp.mkd.called)
        self.assertTrue(mock_log.debug.called)

    def test__create_folder_perm_err(self, mock_log, mock_ftp):
        mock_ftp.ftp.mkd.side_effect = ftplib.error_perm()
        expected = ""
        output = FTPUploader._create_folder(mock_ftp, "test")

        self.assertEqual(expected, output)
        self.assertTrue(mock_ftp.ftp.mkd.called)
        self.assertTrue(mock_log.debug.called)

    @mock.patch('nephos.uploader.ftp.get')
    def test__get_ftp_config_none(self, mock_get, _, __):
        mock_get.return_value = None
        FTPUploader._get_ftp_config()

        self.assertTrue(mock_get.called)
        mock_get.assert_called_with(mock.ANY, 'upload.ftp.host')

    @mock.patch('nephos.uploader.ftp.get')
    def test__get_ftp_config_not_none(self, mock_get, _, __):
        mock_get.return_value = 10
        FTPUploader._get_ftp_config()

        self.assertTrue(mock_get.called)
        mock_get.assert_called_with(mock.ANY, 'upload.ftp.password')

    def test__get_name_file(self, _, __):
        expected = "test.tst"
        output = FTPUploader._get_name('/home/test/test.tst')

        self.assertEqual(expected, output)

    def test__get_name_folder(self, _, __):
        expected = "test"
        output = FTPUploader._get_name('/home/test')

        self.assertEqual(expected, output)
