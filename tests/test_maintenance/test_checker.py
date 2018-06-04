from unittest import TestCase, mock
from nephos.maintenance.checker import Checker


@mock.patch('nephos.maintenance.checker.Checker')
class TestChecker(TestCase):

    def test_to_run_enabled(self, mock_checker):
        mock_checker._get_data.return_value = True
        Checker.to_run(mock_checker, "test")

        self.assertTrue(mock_checker._execute.called)

    @mock.patch('nephos.maintenance.checker.LOG')
    def test_to_run_disabled(self, mock_log, mock_checker):
        mock_checker._get_data.return_value = False
        Checker.to_run(mock_checker, "test")

        mock_log.warning.assert_called_with("%s maintenance job is not enabled", "test")

    @mock.patch('nephos.maintenance.checker.LOG')
    def test__handle_critical(self, mock_log, _):
        msg = "msg"
        Checker._handle(True, msg)

        mock_log.critical.assert_called_with(msg)

    @mock.patch('nephos.maintenance.checker.LOG')
    def test__handle_not_critical(self, mock_log, _):
        msg = "msg"
        Checker._handle(False, msg)

        mock_log.info.assert_called_with(msg)

    def test__get_data(self, mock_checker):
        mock_checker.config.new = {
            'jobs': {
                'test': {
                    'is_pass': True
                }
            }
        }

        return_bool = Checker._get_data(mock_checker, 'test', 'is_pass')

        self.assertTrue(return_bool)
