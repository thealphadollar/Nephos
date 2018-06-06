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


@mock.patch('nephos.recorder.channels.ChannelHandler')
class TestChannelHandler(TestCase):

    @mock.patch('nephos.recorder.channels.DBHandler')
    @mock.patch('nephos.recorder.channels.input')
    def test_add_channel(self, mock_input, mock_db_handler, mock_ch_handler):
        with mock.patch('nephos.recorder.channels.validate_entries'):
            ChannelHandler.add_channel(mock_ch_handler)

            self.assertTrue(mock_input.called)
            self.assertTrue(mock_db_handler.connect.called)
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
        with mock_db_handler.connect() as db_cur:
            ChannelHandler.insert_channels(db_cur, MOCK_CH_DATA)

            self.assertTrue(mock_db_handler.insert_data.called)
            self.assertTrue(mock_log.info.called)
            self.assertTrue(mock_os.makedirs.called)
            self.assertFalse(mock_log.warning.called)

    @mock.patch('nephos.recorder.channels.LOG')
    @mock.patch('nephos.recorder.channels.os')
    @mock.patch('nephos.recorder.channels.DBHandler')
    def test_insert_channels_invalid(self, mock_db_handler, mock_os, mock_log, _):
        mock_db_handler.insert_data.return_value = None
        with mock_db_handler.connect() as db_cur:
            ChannelHandler.insert_channels(db_cur, MOCK_CH_DATA)

            self.assertTrue(mock_db_handler.insert_data.called)
            self.assertFalse(mock_log.info.called)
            self.assertFalse(mock_os.makedirs.called)
            self.assertTrue(mock_log.warning.called)

    @mock.patch('nephos.recorder.channels.input')
    @mock.patch('nephos.recorder.channels.LOG')
    @mock.patch('nephos.recorder.channels.DBHandler')
    def test_delete_channel(self, mock_db_handler, mock_log, mock_input, _):
        mock_input.return_value = "ch_test"
        ChannelHandler.delete_channel()

        self.assertTrue(mock_input.called)
        self.assertTrue(mock_db_handler.connect.called)
        self.assertTrue(mock_log.info.called)
        self.assertFalse(mock_log.warning.called)
        self.assertFalse(mock_log.debug.called)

    @mock.patch('nephos.recorder.channels.input')
    @mock.patch('nephos.recorder.channels.LOG')
    @mock.patch('nephos.recorder.channels.DBHandler')
    def test_delete_channel_error(self, mock_db_handler, mock_log, mock_input, _):
        mock_input.return_value = "ch_test"
        mock_db_handler.connect.side_effect = Error
        ChannelHandler.delete_channel()

        self.assertTrue(mock_input.called)
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
    def test_record_stream(self, mock_log, mock_subprocess, _):
        with mock.patch('nephos.recorder.channels._is_up', return_value=True):
            ChannelHandler.record_stream('0.0.0.0', 'test', 0)

            self.assertTrue(mock_subprocess.check_call.called)
            self.assertFalse(mock_log.warning.called)
            self.assertFalse(mock_log.debug.called)

    @mock.patch('nephos.recorder.channels.subprocess')
    @mock.patch('nephos.recorder.channels.LOG')
    def test_record_stream_error(self, mock_log, mock_subprocess, _):
        mock_subprocess.check_call.side_effect = subprocess.CalledProcessError
        mock_subprocess.CalledProcessError = Exception
        with mock.patch('nephos.recorder.channels._is_up', return_value=True):
            ChannelHandler.record_stream('0.0.0.0', 'test', 0)

            self.assertTrue(mock_subprocess.check_call.called)
            self.assertTrue(mock_log.warning.called)
            self.assertTrue(mock_log.debug.called)

    @mock.patch('nephos.recorder.channels.DBHandler')
    def test__is_up(self, mock_db_handler, _):
        return_bool = _is_up('0.0.0.0')

        self.assertTrue(mock_db_handler.connect.called)
        self.assertFalse(return_bool)
