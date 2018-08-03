from unittest import TestCase, mock
from sqlite3 import Error
import subprocess
from nephos.recorder.channels import ChannelHandler, _is_up
from nephos.exceptions import DBException

MOCK_CH_TUPLE = (
    ("0", "ch_test", "0.0.0.0:8080")
)

MOCK_CH_DATA = {
    '0': {
        'name': 'ch_test'
    }
}

MOCK_RECORDER_CONFIG = {
    'path_to_multicat': 'path',
    'ifaddr': ''
}


@mock.patch('nephos.recorder.channels.ChannelHandler')
class TestChannelHandler(TestCase):

    @mock.patch('nephos.recorder.channels.input')
    def test_add_channel(self, mock_input, mock_ch_handler):
        with mock.patch('nephos.recorder.channels.validate_entries'):
            ChannelHandler.add_channel(mock_ch_handler)

            self.assertTrue(mock_input.called)
            self.assertTrue(mock_ch_handler.insert_channels.called)

    @mock.patch('nephos.recorder.channels.LOG')
    def test_display_channel(self, mock_log, mock_ch_handler):
        mock_ch_handler.grab_ch_list.return_value = MOCK_CH_TUPLE
        ChannelHandler.display_channel(mock_ch_handler)

        self.assertTrue(mock_ch_handler.grab_ch_list.called)
        self.assertTrue(mock_log.info.called)

    @mock.patch('nephos.recorder.channels.LOG')
    @mock.patch('nephos.recorder.channels.os')
    @mock.patch('nephos.recorder.channels.DBHandler')
    def test_insert_channels_correct(self, mock_db_handler, mock_os, mock_log, _):
        mock_db_handler.insert_data.return_value = 0
        ChannelHandler.insert_channels(MOCK_CH_DATA)

        self.assertTrue(mock_db_handler.insert_data.called)
        self.assertTrue(mock_log.info.called)
        self.assertTrue(mock_os.makedirs.called)
        self.assertFalse(mock_log.warning.called)

    @mock.patch('nephos.recorder.channels.LOG')
    @mock.patch('nephos.recorder.channels.os')
    @mock.patch('nephos.recorder.channels.DBHandler')
    def test_insert_channels_invalid(self, mock_db_handler, mock_os, mock_log, _):
        mock_db_handler.insert_data.return_value = None

        ChannelHandler.insert_channels(MOCK_CH_DATA)

        self.assertTrue(mock_db_handler.insert_data.called)
        self.assertFalse(mock_log.info.called)
        self.assertFalse(mock_os.makedirs.called)

    @mock.patch('nephos.recorder.channels.LOG')
    @mock.patch('nephos.recorder.channels.DBHandler')
    def test_delete_channel(self, mock_db_handler, mock_log, _):
        ChannelHandler.delete_channel()

        self.assertTrue(mock_db_handler.connect.called)
        self.assertTrue(mock_log.info.called)
        self.assertFalse(mock_log.warning.called)
        self.assertFalse(mock_log.debug.called)

    @mock.patch('nephos.recorder.channels.LOG')
    @mock.patch('nephos.recorder.channels.DBHandler')
    def test_delete_channel_error(self, mock_db_handler, mock_log, _):
        mock_db_handler.connect.side_effect = Error
        with self.assertRaises(IOError):
            ChannelHandler.delete_channel()

            self.assertTrue(mock_db_handler.connect.called)
            self.assertFalse(mock_log.info.called)
            self.assertTrue(mock_log.warning.called)
            self.assertTrue(mock_log.debug.called)

    @mock.patch('nephos.recorder.channels.LOG')
    @mock.patch('nephos.recorder.channels.DBHandler')
    def test_grab_ch_list(self, mock_db_handler, mock_log, _):
        ChannelHandler.grab_ch_list()

        self.assertTrue(mock_db_handler.connect.called)
        self.assertFalse(mock_log.warning.called)
        self.assertFalse(mock_log.debug.called)

    @mock.patch('nephos.recorder.channels.LOG')
    @mock.patch('nephos.recorder.channels.DBHandler')
    def test_grab_ch_list_error(self, mock_db_handler, mock_log, _):
        mock_db_handler.connect.side_effect = DBException
        ChannelHandler.grab_ch_list()

        self.assertTrue(mock_db_handler.connect.called)
        self.assertTrue(mock_log.warning.called)
        self.assertTrue(mock_log.debug.called)

    @mock.patch('nephos.recorder.channels.subprocess')
    @mock.patch('nephos.recorder.channels.LOG')
    @mock.patch('nephos.recorder.channels.add_to_report')
    def test_record_stream_error(self, mock_add_report, mock_log, mock_subprocess, _):
        mock_subprocess.Popen.side_effect = subprocess.CalledProcessError
        mock_subprocess.CalledProcessError = Exception
        with mock.patch('nephos.recorder.channels._is_up', return_value=True), \
                mock.patch('nephos.recorder.channels.get_recorder_config', return_value=MOCK_RECORDER_CONFIG):
            ChannelHandler.record_stream('0.0.0.0', 'test', 0)

            self.assertTrue(mock_subprocess.Popen.called)
            self.assertTrue(mock_log.warning.called)
            self.assertTrue(mock_log.debug.called)
            self.assertTrue(mock_add_report.called)

    @mock.patch('nephos.recorder.channels.DBHandler')
    def test__is_up(self, mock_db_handler, _):
        return_bool = _is_up('0.0.0.0')

        self.assertTrue(mock_db_handler.connect.called)
        self.assertFalse(return_bool)
