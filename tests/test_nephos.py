from unittest import TestCase, mock
from nephos.nephos import Nephos, DBException


@mock.patch('nephos.nephos.Nephos')
@mock.patch('nephos.nephos.LOG')
class TestNephos(TestCase):

    @mock.patch('nephos.nephos.Config')
    @mock.patch('nephos.nephos.DBHandler')
    @mock.patch('nephos.nephos.Scheduler')
    @mock.patch('nephos.nephos.ChannelHandler')
    @mock.patch('nephos.nephos.JobHandler')
    @mock.patch('nephos.nephos.Maintenance')
    def test_init(self, mock_maintenance, mock_job, mock_ch, mock_scheduler,
                  mock_db, mock_config, mock_log, mock_nephos):
        with mock.patch('nephos.nephos.first_time', return_value=True):
            Nephos()

            self.assertTrue(mock_config.called)
            self.assertTrue(mock_db.called)
            self.assertTrue(mock_scheduler.called)
            self.assertTrue(mock_ch.called)
            self.assertTrue(mock_job.called)
            self.assertTrue(mock_maintenance.called)
            mock_log.info.assert_called_with("Nephos is all set to launch")

    def test_start(self, mock_log, mock_nephos):
        Nephos.start(mock_nephos)

        self.assertTrue(mock_nephos.scheduler.start.called)
        self.assertTrue(mock_log.info.called)

    @mock.patch('nephos.nephos.input')
    def test_load_channels_sharelist(self, mock_input, mock_log, mock_nephos):
        Nephos.load_channels_sharelist(mock_nephos)

        mock_input.assert_called_with("File path: ")
        mock_nephos.config_handler.load_data.asset_called_with(mock.ANY, mock.ANY)
        self.assertTrue(mock_nephos.db_handler.connect.called)
        self.assertTrue(mock_nephos.channel_handler.insert_channels.called)
        self.assertFalse(mock_log.warning.called)
        self.assertFalse(mock_log.error.called)

    @mock.patch('nephos.nephos.input')
    def test_load_channels_sharelist_key_error(self, mock_input, mock_log, mock_nephos):
        mock_nephos.channel_handler.insert_channels.side_effect = KeyError
        Nephos.load_channels_sharelist(mock_nephos)

        mock_input.assert_called_with("File path: ")
        mock_nephos.config_handler.load_data.asset_called_with(mock.ANY, mock.ANY)
        self.assertTrue(mock_nephos.db_handler.connect.called)
        self.assertTrue(mock_nephos.channel_handler.insert_channels.called)
        self.assertTrue(mock_log.warning.called)
        self.assertTrue(mock_log.error.called)

    @mock.patch('nephos.nephos.input')
    def test_load_channels_sharelist_DBException(self, mock_input, mock_log, mock_nephos):
        mock_nephos.db_handler.connect.side_effect = DBException
        Nephos.load_channels_sharelist(mock_nephos)

        mock_input.assert_called_with("File path: ")
        mock_nephos.config_handler.load_data.asset_called_with(mock.ANY, mock.ANY)
        self.assertTrue(mock_nephos.db_handler.connect.called)
        self.assertFalse(mock_nephos.channel_handler.insert_channels.called)
        self.assertTrue(mock_log.warning.called)
        self.assertTrue(mock_log.error.called)
