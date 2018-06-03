from unittest import TestCase, mock
import os
import tempfile
from io import StringIO
from nephos import __nephos_dir__, __config_dir__, __log_dir__, __db_dir__, \
    __recording_dir__, __upload_dir__, __docs_dir__, first_time, validate_entries

mock_wrong_data = {
    '0': {
        'email': 'abc@xyz.com abc.com',
        'ip': '0.0.0.0:8080',
        'country_code': 'IND USA',
        'language': 'ENG',
        'timezone': 'UTC',
        'start_time': '05:00',
        'duration': '17',
        'repetition': '0000000'
    }
}

mock_correct_data = {
    '0': {
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
            with mock.patch('nephos.__nephos_dir__', new=os.path.join(temp_dir)):
                self.assertFalse(first_time())

    @mock.patch('os.path.exists', return_value=False)
    @mock.patch('nephos.copy_tree')
    def test_first_time_true(self, mock_exists, mock_copy):
        with mock.patch('os.makedirs') as mock_makedir:
            self.assertTrue(first_time())

            mock_makedir.mock_calls[0] = [mock.call(__nephos_dir__)]
            mock_makedir.mock_calls[1] = [mock.call(__config_dir__)]
            mock_makedir.mock_calls[2] = [mock.call(__log_dir__)]
            mock_makedir.mock_calls[3] = [mock.call(__db_dir__)]
            mock_makedir.mock_calls[4] = [mock.call(__recording_dir__)]
            mock_makedir.mock_calls[5] = [mock.call(__upload_dir__)]
            mock_makedir.mock_calls[6] = [mock.call(__docs_dir__)]


class TestValidateEntries(TestCase):

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_validate_entries(self, mock_output):
        with mock.patch('nephos.input', return_value='abc@xyz.com'):
            correct_data = validate_entries('test', mock_wrong_data)
            self.assertDictEqual(correct_data, mock_correct_data)

            output = mock_output.getvalue()
            expected_output = "abc.com incorrect\n"
            self.assertEqual(output, expected_output)


