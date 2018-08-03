from unittest import TestCase, mock
import os
import tempfile
from io import StringIO
from nephos import __nephos_dir__, __config_dir__, __log_dir__, __db_dir__, \
    __recording_dir__, __upload_dir__, __docs_dir__, first_time, \
    validate_entries, load_mail_list

MOCK_WRONG_DATA = {
    '0': {
        'email': 'abc@xyz.com abc.com',
        'ip': '0.0.0.0:8080',
        'country_code': 'IND USA',
        'language': 'ENG',
        'timezone': 'UTC',
        'start_time': '05:00',
        'duration': '17',
        'repetition': '0000000'
    },
    '1': {
        'email': 'abc@xyz.com',
        'ip': '0.0.0.0:8080',
        'country_code': 'IND USA',
        'language': 'ENG',
        'timezone': 'UTC',
        'start_time': '05:00',
        'duration': '17',
        'repetition': '0000000'
    }
}

MOCK_CORRECT_DATA = {
    '1': {
        'email': 'abc@xyz.com',
        'ip': '0.0.0.0:8080',
        'country_code': 'IND USA',
        'language': 'ENG',
        'timezone': 'UTC',
        'start_time': '05:00',
        'duration': '17',
        'repetition': '0000000'
    }
}


class TestFirstTime(TestCase):

    def test_first_time_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch('nephos.__nephos_dir__', new=temp_dir):
                self.assertFalse(first_time())

    @mock.patch('nephos.load_mail_list')
    @mock.patch('nephos.copy_tree')
    @mock.patch('os.makedirs')
    def test_first_time_true(self, mock_makedir, mock_copy, mock_load_mail):
        with mock.patch('os.path.exists', return_value=False):
            self.assertTrue(first_time())

            mock_makedir.mock_calls[0] = [mock.call(__nephos_dir__)]
            mock_makedir.mock_calls[1] = [mock.call(__config_dir__)]
            mock_makedir.mock_calls[2] = [mock.call(__log_dir__)]
            mock_makedir.mock_calls[3] = [mock.call(__db_dir__)]
            mock_makedir.mock_calls[4] = [mock.call(__recording_dir__)]
            mock_makedir.mock_calls[5] = [mock.call(__upload_dir__)]
            mock_makedir.mock_calls[6] = [mock.call(__docs_dir__)]
            self.assertTrue(mock_copy.called)
            self.assertTrue(mock_load_mail.called)

    @mock.patch('nephos.input')
    def test_load_mail_list(self, mock_input):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "email_test")

            # initially temp_file doesn't exist
            with mock.patch('nephos.CRITICAL_MAIL_ADDRS_PATH', new=temp_file):
                with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                    mock_input.return_value = "shivam.cs.iit.kgp@gmail.com shiv"
                    load_mail_list()
                    output = mock_out.getvalue()
                    expected_output = [
                        "No critical mail list file found!",
                        "Following emails removed from critical mail list due to wrong format!",
                        "['shiv']\n"
                    ]
                    self.assertEqual(output, "\n".join(expected_output))

                # now temp_file exists
                with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                    load_mail_list()
                    output = mock_out.getvalue()
                    expected_output = [
                        "Following emails removed from critical mail list due to wrong format!",
                        "['shiv']\n"
                    ]
                    self.assertEqual(output, "\n".join(expected_output))


class TestValidateEntries(TestCase):

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_validate_entries(self, mock_output):
        correct_data = validate_entries(MOCK_WRONG_DATA)
        self.assertDictEqual(correct_data, MOCK_CORRECT_DATA)

        output = mock_output.getvalue()
        expected_output = "abc.com incorrect\n"
        self.assertEqual(output, expected_output)
