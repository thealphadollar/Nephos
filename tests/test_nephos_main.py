from unittest import TestCase, mock
from io import StringIO
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerNotRunningError
from click.testing import CliRunner
from nephos.__main__ import runtime_help, stop, print_ver_info, start, multi_key_dict_get


MOCK_MULTI_KEY_DICT = {
    ("key1", "key2"): "pass"
}


class TestRuntimeHelp(TestCase):

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_runtime_help(self, mock_output):
        runtime_help()
        output = mock_output.getvalue()
        expected_str = 'show help'

        self.assertIn(expected_str, output)


class TestStop(TestCase):

    def test_stop_if_running(self):
        scheduler = BackgroundScheduler()
        scheduler.start()
        self.assertTrue(scheduler.running)

        stop(scheduler)
        self.assertFalse(scheduler.running)

    def test_stop_not_running(self):
        scheduler = BackgroundScheduler()

        with self.assertRaises(SchedulerNotRunningError):
            stop(scheduler)


class TestStart(TestCase):
    @mock.patch('nephos.__main__.Nephos')
    @mock.patch('nephos.__main__.LOG')
    def test_start(self, mock_log, mock_nephos):
        runner = CliRunner()
        runner.invoke(start, input='quit')
        expected = "Nephos Stopped!"

        self.assertTrue(mock_nephos.called)
        mock_log.warning.assert_called_with(expected)


class TestPrintVerInfo(TestCase):

    def test_print_ver_info(self):
        runner = CliRunner()
        result = runner.invoke(print_ver_info)
        expected_output = "__title__ = 'Nephos'"

        self.assertIn(expected_output, result.output)


class TestMultiKeyDictGet(TestCase):

    def test_multi_key_present(self):
        value = multi_key_dict_get(MOCK_MULTI_KEY_DICT, "key1")
        expected_value = "pass"
        self.assertEqual(value, expected_value)

    def test_multi_key_absent(self):
        value = multi_key_dict_get(MOCK_MULTI_KEY_DICT, "key3")

        self.assertIsNone(value)
