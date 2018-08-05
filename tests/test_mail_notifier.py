import subprocess
from unittest import TestCase, mock
from nephos.mail_notifier import send_mail, send_report, add_to_report

MOCK_REPORT_FILE = 'report.txt'


class MockPopen:
    def __init__(self, cmd, shell, stdout, stderr):
        pass

    @staticmethod
    def communicate():
        return "some text", "some other text"


@mock.patch('nephos.mail_notifier.LOG')
class TestMailNotifier(TestCase):

    @mock.patch('nephos.mail_notifier.subprocess')
    @mock.patch('nephos.mail_notifier.load_mail_list', return_value='test')
    def test_send_mail(self, mock_mails, mock_subprocess, mock_log):
        mock_subprocess.Popen.side_effect = MockPopen
        return_value = send_mail("test", "critical")

        self.assertTrue(mock_mails.called)
        self.assertTrue(mock_subprocess.Popen.called)
        self.assertTrue(mock_log.debug.called)
        self.assertEqual(return_value, True)

    @mock.patch('nephos.mail_notifier.subprocess')
    @mock.patch('nephos.mail_notifier.load_mail_list', return_value='test')
    def test_send_mail_error(self, mock_mails, mock_subprocess, mock_log):
        mock_subprocess.Popen.side_effect = subprocess.CalledProcessError(1, cmd="test")
        mock_subprocess.CalledProcessError = subprocess.CalledProcessError
        return_value = send_mail("test", "critical")

        self.assertTrue(mock_mails.called)
        self.assertTrue(mock_subprocess.Popen.called)
        self.assertTrue(mock_log.warning.called)
        self.assertEqual(return_value, False)

    @mock.patch('nephos.mail_notifier.open')
    def test_add_to_report(self, mock_open, mock_log):
        add_to_report("test")

        self.assertFalse(mock_log.called)
        mock_open.assert_called_with(mock.ANY, "a")

    @mock.patch('nephos.mail_notifier.open')
    @mock.patch('nephos.mail_notifier.send_mail')
    @mock.patch('nephos.mail_notifier.os')
    def test_send_report(self, mock_os, mock_mail, mock_open, mock_log):
        send_report()

        self.assertFalse(mock_log.called)
        mock_open.assert_called_with(mock.ANY, "r")
        self.assertTrue(mock_os.remove.called)
        self.assertTrue(mock_mail.called)
