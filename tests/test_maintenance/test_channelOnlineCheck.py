from unittest import TestCase, mock
from nephos.maintenance.channel_online_check import ChannelOnlineCheck


# passed as last argument to all functions
@mock.patch('nephos.maintenance.channel_online_check.ChannelOnlineCheck')
class TestChannelOnlineCheck(TestCase):

    @mock.patch('nephos.maintenance.channel_online_check.Checker.__init__')
    def test_init(self, mock_checker, _):
        channel_checker = ChannelOnlineCheck(mock.ANY)
        self.assertTrue(mock_checker.called)
        self.assertIsNone(channel_checker.channel_list)

    @mock.patch('nephos.maintenance.channel_online_check.POOL')
    @mock.patch('nephos.maintenance.channel_online_check.DBHandler')
    @mock.patch('nephos.maintenance.channel_online_check.ChannelHandler')
    def test__execute(self, mock_ch, mock_db, mock_pool, mock_channel_checker):
        mock_channel_checker._extract_ips.return_value = ['0.0.0.0']
        ChannelOnlineCheck._execute(mock_channel_checker)

        self.assertTrue(mock_ch.grab_ch_list.called)
        self.assertTrue(mock_channel_checker._channel_stats.called)
        self.assertTrue(mock_channel_checker._extract_ips.called)
        self.assertTrue(mock_db.connect.called)
        mock_pool.starmap.assert_called_with(mock.ANY, mock.ANY)
        self.assertTrue(mock_pool.close.called)
        self.assertTrue(mock_pool.join.called)

#
#     def test__check_ip(self):
#         self.fail()
#
#     def test__channel_stats(self):
#         self.fail()
#
#     def test__extract_ips(self):
#         self.fail()
#
#     def test__formulate_report(self):
#         self.fail()
#
#     def test__universal_worker(self):
#         self.fail()
#
#     def test__pool_args(self):
#         self.fail()
