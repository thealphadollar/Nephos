import os
from unittest import TestCase
from unittest import mock
from io import StringIO
from nephos.load_config import get_env_var
from nephos.load_config import Config
import pydash


def mock_load(to_load, _=True):
    """
    Mocks the load function from Config Class

    Parameters
    ----------
    to_load
        type: str
        configuration to load
    _
        type: bool

    Returns
    -------
    type: dict
    configuration for each module

    """
    data = {
        "logging.yaml":
            {
                "version": 1
            },
        "maintenance.yaml":
            {
                "version": 1
            },
        "preprocess.yaml":
            {
                "version": 1
            },
        "uploader.yaml":
            {
                "version": 1
            }
    }
    return data[to_load]


class TestConfig(TestCase):

    TestConfig = Config()

    def test_initial_data_none(self):

        self.assertIsNone(self.TestConfig.logging_config)
        self.assertIsNone(self.TestConfig.maintenance_config)
        self.assertIsNone(self.TestConfig.preprocess_config)
        self.assertIsNone(self.TestConfig.uploader_config)

    @mock.patch('nephos.load_config.Config.load_data', side_effect=mock_load)
    @mock.patch('nephos.load_config.Config._correct_log_file_path', return_value="correct_path")
    @mock.patch('nephos.load_config.Config.load_mail_list', return_value=["abc@xyz.com"])
    @mock.patch('nephos.load_config.get_env_var', return_value="env_value")
    def test_load_config(self, mock_load_config, mock_correct_path, mock_mail_list, mock_load_env):

        self.TestConfig.load_config()

        self.assertIsInstance(self.TestConfig.logging_config, dict)
        self.assertIsInstance(self.TestConfig.maintenance_config, dict)
        self.assertIsInstance(self.TestConfig.preprocess_config, dict)
        self.assertIsInstance(self.TestConfig.uploader_config, dict)

        # =============================================
        # below tests check for the correction of input
        log_version = pydash.get(self.TestConfig.logging_config, "version")
        maintainer_version = pydash.get(self.TestConfig.maintenance_config, "version")
        preprocessor_version = pydash.get(self.TestConfig.preprocess_config, "version")
        uploader_version = pydash.get(self.TestConfig.uploader_config, "version")

        self.assertEqual(log_version, 1)
        self.assertEqual(maintainer_version, 1)
        self.assertEqual(preprocessor_version, 1)
        self.assertEqual(uploader_version, 1)
        # =============================================

        # =============================================
        # below tests pass if _config_updates works fine
        nephos_log_file = pydash.get(self.TestConfig.logging_config, 'handlers.nephos_file.filename')
        email_addr = pydash.get(self.TestConfig.logging_config, 'handlers.email.toaddrs')
        credentials = pydash.get(self.TestConfig.logging_config, 'handlers.email.credentials')

        expected_nephos_log_file = "correct_path"
        expected_email_addr = ["abc@xyz.com"]
        expected_credentials = ("env_value", "env_value")

        self.assertEqual(nephos_log_file, expected_nephos_log_file)
        self.assertEqual(email_addr, expected_email_addr)
        self.assertEqual(credentials, expected_credentials)
        # =============================================
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
