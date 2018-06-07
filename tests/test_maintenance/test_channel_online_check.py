from unittest import TestCase, mock
from multiprocessing import pool
from functools import partial
from nephos.maintenance.channel_online_check import ChannelOnlineCheck


MOCK_POOL = pool.ThreadPool(2)


class MockOSReturn:
    def __init__(self, value):
        self.st_size = value


MOCK_CH_LIST = (
    ("ch_up", "0.0.0.0", "up"),
    ("ch_down", '127.0.0.1', "down")
)

MOCK_PREV_STATS = {
    "down_ch": 1,
    "down_ch_names": ["ch_down::0.0.0.0"],
    "up_ch": 1
}

MOCK_NEW_STATS = {
    "down_ch": 2,
    "down_ch_names": ["ch_down::0.0.0.0", "ch_up::127.0.0.1"],
    "up_ch": 1
}


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
        mock_pool.map.assert_called_with(mock.ANY, mock.ANY)

    @mock.patch('nephos.maintenance.channel_online_check.DBHandler')
    @mock.patch('nephos.maintenance.channel_online_check.ChannelHandler')
    @mock.patch('os.stat')
    @mock.patch('nephos.maintenance.channel_online_check.LOG')
    def test__check_ip(self, mock_log, mock_stat, mock_ch, mock_db, _):
        mock_stat.return_value = MockOSReturn(0)
        ip_addr = '0.0.0.0:8080'
        with mock_db.connect() as db_cur:
            ChannelOnlineCheck._check_ip(ip_addr, db_cur, 'test')

            mock_ch.record_stream.assert_called_with(mock.ANY, mock.ANY, mock.ANY, test=True)
            self.assertTrue(mock_stat.called)
            db_cur.execute.assert_called_with(mock.ANY, mock.ANY)
            mock_log.debug.assert_called_with("Channel with ip: %s down", ip_addr)

    def test__channel_stats(self, mock_channel_checker):
        with mock.patch('nephos.maintenance.channel_online_check.ChannelOnlineCheck.channel_list',
                        new=MOCK_CH_LIST), \
             mock.patch('nephos.maintenance.channel_online_check.CH_NAME_INDEX', new=0), \
             mock.patch('nephos.maintenance.channel_online_check.CH_IP_INDEX', new=1), \
             mock.patch('nephos.maintenance.channel_online_check.CH_STAT_INDEX', new=2):
            out_dict = ChannelOnlineCheck._channel_stats(mock_channel_checker)

            self.assertIsInstance(out_dict, dict)
            self.assertEqual(out_dict['down_ch'], 1)
            self.assertEqual(out_dict['down_ch_names'], ['ch_down::127.0.0.1'])
            self.assertEqual(out_dict['up_ch'], 1)

    def test__extract_ips(self, mock_channel_checker):
        with mock.patch('nephos.maintenance.channel_online_check.ChannelOnlineCheck.channel_list',
                        new=MOCK_CH_LIST), \
             mock.patch('nephos.maintenance.channel_online_check.CH_IP_INDEX', new=1):
            ip_list = ChannelOnlineCheck._extract_ips(mock_channel_checker)

            self.assertIsInstance(ip_list, list)
            self.assertEqual(ip_list, ['0.0.0.0', '127.0.0.1'])

    def test__formulate_report_no_change(self, _):
        report = ChannelOnlineCheck._formulate_report(MOCK_PREV_STATS, MOCK_PREV_STATS)

        self.assertFalse(report[0])
        self.assertEqual(report[1], "No new down channels!")

    def test__formulate_report_change(self, _):
        report = ChannelOnlineCheck._formulate_report(MOCK_PREV_STATS, MOCK_NEW_STATS)

        self.assertTrue(report[0])
        self.assertIn("Following 2 channel(s) are down:", report[1])

    def test__pool_args(self, mock_channel_checker):
        """
        Tests the multiprocessing's pool for correct argument passing, doesn't concern any nephos's
        module directly

        Parameters
        ----------
        mock_channel_checker
            type: MagicMock
            mock class of ChannelOnlineCheck

        Returns
        -------

        """
        db_cur = "test"
        ips = ['0.0.0.0', '127.0.0.1']
        tmpdir = "test"
        MOCK_POOL.map(partial(mock_channel_checker, arg2=db_cur, arg3=tmpdir), ips)
        MOCK_POOL.close()
        MOCK_POOL.join()

        self.assertTrue(mock_channel_checker.called)
        mock_channel_checker.has_any_call(ips[0], arg2=db_cur, arg3=tmpdir)
        mock_channel_checker.has_any_call(ips[1], arg2=db_cur, arg3=tmpdir)
