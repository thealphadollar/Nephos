import os
from unittest import TestCase
from unittest import mock
from io import StringIO
from nephos.load_config import get_env_var


# class TestConfig(TestCase):
#     def test_load_config(self):
#         self.fail()
#
#     def test_initialise(self):
#         self.fail()
#
#     def test_load_data(self):
#         self.fail()
#
#     def test__correct_log_file_path(self):
#         self.fail()
#
#     def test__config_update(self):
#         self.fail()
#
#     def test_load_mail_list(self):
#         self.fail()


class TestGetEnvVar(TestCase):

    def test_getting_existing_env_var(self):
        os.environ["NEPHOS_TEST"] = "running"
        return_value = get_env_var("NEPHOS_TEST")
        expected_value = os.environ.get("NEPHOS_TEST")
        del os.environ["NEPHOS_TEST"]
        self.assertEqual(return_value, expected_value)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_getting_non_existing_env_var(self, mock_output):
        var_name = "NEPHOS_TEST"
        get_env_var(var_name)
        output = mock_output.getvalue()
        expected_output = ("Warning: Environment variable {env_name} not set! "
                           "Some functions might not work properly!\n".format(env_name=var_name))
        self.assertEqual(output, expected_output)
