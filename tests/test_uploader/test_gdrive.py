from unittest import TestCase, mock

from googleapiclient.http import UnexpectedBodyError

from nephos.uploader.gdrive import GDrive, OAuthFailure


class Credentials:
    def __init__(self):
        self.invalid = False


class Response:
    @staticmethod
    def get(_):
        return "test"


@mock.patch('nephos.uploader.gdrive.GDrive')
@mock.patch('nephos.uploader.gdrive.LOG')
class TestGDrive(TestCase):

    @mock.patch('nephos.uploader.gdrive.file')
    @mock.patch('nephos.uploader.gdrive.discovery')
    @mock.patch('nephos.uploader.gdrive.send_mail')
    def test_auth(self, mock_mail, mock_discovery, mock_file, mock_log, mock_drive):
        GDrive.auth(mock_drive)

        self.assertTrue(mock_file.Storage.called)
        self.assertTrue(mock_drive._auth_from_file.called)
        self.assertTrue(mock_log.info.called)
        self.assertFalse(mock_drive._init_auth_flow.called)
        self.assertTrue(mock_discovery.build.called)
        self.assertFalse(mock_log.critical.called)
        self.assertFalse(mock_mail.called)

    @mock.patch('nephos.uploader.gdrive.file')
    @mock.patch('nephos.uploader.gdrive.discovery')
    @mock.patch('nephos.uploader.gdrive.send_mail')
    def test_auth_fail_file(self, mock_mail, mock_discovery, mock_file, mock_log, mock_drive):
        mock_drive._auth_from_file.side_effect = OAuthFailure()
        GDrive.auth(mock_drive)

        self.assertTrue(mock_file.Storage.called)
        self.assertTrue(mock_drive._auth_from_file.called)
        self.assertFalse(mock_log.info.called)
        self.assertTrue(mock_drive._init_auth_flow.called)
        self.assertTrue(mock_discovery.build.called)
        self.assertFalse(mock_log.critical.called)
        self.assertFalse(mock_mail.called)

    @mock.patch('nephos.uploader.gdrive.discovery')
    def test__get_upload_service(self, mock_discovery, _, mock_drive):
        GDrive._get_upload_service()

        self.assertTrue(mock_drive._auth_from_file.called)
        self.assertTrue(mock_discovery.build.called)

    @mock.patch('nephos.uploader.gdrive.DBHandler')
    @mock.patch('nephos.uploader.gdrive.add_to_report')
    def test__upload(self, mock_report, mock_db, mock_log, mock_drive):
        tasks_list = ["test task"]
        mock_drive._create_folder.return_value = "test"
        GDrive._upload(tasks_list)

        self.assertTrue(mock_drive._get_upload_service.called)
        self.assertTrue(mock_drive._set_uploading.called)
        self.assertTrue(mock_drive._create_folder.called)
        self.assertTrue(mock_drive._upload_files.called)
        self.assertTrue(mock_drive._share.called)
        self.assertTrue(mock_log.debug.called)
        self.assertTrue(mock_drive._remove.called)
        self.assertTrue(mock_report.called)
        self.assertFalse(mock_db.connect.called)

    @mock.patch('nephos.uploader.gdrive.DBHandler')
    @mock.patch('nephos.uploader.gdrive.add_to_report')
    def test__upload_folder_fails(self, mock_report, mock_db, mock_log, mock_drive):
        tasks_list = ["test task"]
        mock_drive._create_folder.return_value = None
        mock_drive._upload_files.side_effect = UnexpectedBodyError("test", "text")
        GDrive._upload(tasks_list)

        self.assertTrue(mock_drive._get_upload_service.called)
        self.assertTrue(mock_drive._set_uploading.called)
        self.assertTrue(mock_drive._create_folder.called)
        self.assertTrue(mock_drive._upload_files.called)
        self.assertFalse(mock_drive._share.called)
        self.assertTrue(mock_log.debug.called)
        self.assertFalse(mock_drive._remove.called)
        self.assertTrue(mock_report.called)
        self.assertTrue(mock_db.connect.called)

    @mock.patch('nephos.uploader.gdrive.os')
    @mock.patch('nephos.uploader.gdrive.shutil')
    def test_upload_log(self, mock_shutil, mock_os, mock_log, mock_drive):
        GDrive.upload_log(mock_drive)

        self.assertTrue(mock_os.path.join.called)
        self.assertTrue(mock_shutil.copyfile.called)
        self.assertTrue(mock_drive._upload_file.called)
        self.assertTrue(mock_log.debug.called)
        self.assertFalse(mock_log.warning.called)
        self.assertTrue(mock_os.remove.called)

    @mock.patch('nephos.uploader.gdrive.os')
    @mock.patch('nephos.uploader.gdrive.shutil')
    def test_upload_log_fails(self, mock_shutil, mock_os, mock_log, mock_drive):
        mock_drive._upload_file.return_value = None
        GDrive.upload_log(mock_drive)

        self.assertTrue(mock_os.path.join.called)
        self.assertTrue(mock_shutil.copyfile.called)
        self.assertTrue(mock_drive._upload_file.called)
        self.assertFalse(mock_log.debug.called)
        self.assertTrue(mock_log.warning.called)
        self.assertTrue(mock_os.remove.called)

    def test__auth_from_file(self, mock_log, mock_drive):
        mock_drive.get.return_value = Credentials()
        GDrive._auth_from_file(mock_drive)

        self.assertTrue(mock_drive.get.called)
        self.assertFalse(mock_log.warning.called)

    def test__auth_from_file_fail(self, mock_log, mock_drive):
        with self.failUnlessRaises(OAuthFailure):
            GDrive._auth_from_file(mock_drive)

        self.assertTrue(mock_drive.get.called)
        self.assertTrue(mock_log.warning.called)

    @mock.patch('nephos.uploader.gdrive.client')
    @mock.patch('nephos.uploader.gdrive.input')
    def test__init_auth_flow(self, mock_input, mock_client, mock_log, _):
        GDrive._init_auth_flow()

        self.assertTrue(mock_client.flow_from_clientsecrets.called)
        self.assertFalse(mock_log.error.called)
        self.assertTrue(mock_log.critical.called)
        self.assertTrue(mock_input.called)

    def test__create_folder(self, mock_log, mock_drive):
        GDrive._create_folder(mock_drive, "test")

        self.assertTrue(mock_drive._get_name.called)
        self.assertTrue(mock_drive.create.called)
        self.assertTrue(mock_log.debug.called)

    @mock.patch('nephos.uploader.gdrive.os')
    def test__upload_files(self, mock_os, _, mock_drive):
        GDrive._upload_files(mock_drive, "test", "test")

        self.assertTrue(mock_os.path.join.called)
        self.assertTrue(mock_os.listdir.called)

    @mock.patch('nephos.uploader.gdrive.MediaFileUpload')
    def test_upload_file(self, mock_media, mock_log, mock_drive):
        GDrive._upload_file(mock_drive, "test", "test")

        self.assertTrue(mock_drive._get_name.called)
        self.assertTrue(mock_media.called)
        self.assertTrue(mock_drive.create.called)
        self.assertTrue(mock_log.debug.called)

    def test__share(self, _, mock_drive):
        GDrive._share(mock_drive, mock_drive, "test", "test")

        self.assertTrue(mock_drive.add.called)
        self.assertTrue(mock_drive.execute.called)

    def test__get_mimetype_video(self, _, __):
        expected = "video/mp4"
        output = GDrive._get_mimetype('/home/user/test.mp4')

        self.assertEqual(expected, output)

    def test__share_callback(self, mock_log, _):
        GDrive._share_callback(None, Response(), None)

        self.assertTrue(mock_log.debug.called)

    def test__share_callback_error(self, mock_log, _):
        GDrive._share_callback(None, None, "test")

        self.assertTrue(mock_log.debug.called)


