import os
from unittest import TestCase
from unittest import mock
from io import StringIO
import tempfile
import pytest
import pydash
import yaml
from nephos.load_config import get_env_var
from nephos.load_config import Config
from nephos import __nephos_dir__


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


def create_mock_yaml(dir_name):
    """
    Creates mock yaml files in the given dir

    Parameters
    ----------
    dir_name
        type: str
        name of the directory

    Returns
    -------
    type: tuple
    containing path to correct and incorrect yaml file directories

    """
    config_path = os.path.join(dir_name, "config")
    default_config_path = os.path.join(dir_name, "default")

    os.makedirs(config_path, exist_ok=True)
    os.makedirs(default_config_path, exist_ok=True)
    incorrect = os.path.join(config_path, "test.yaml")
    correct = os.path.join(default_config_path, "test.yaml")

    with open(incorrect, "w+") as file:
        file.write("---\nversion\\\\: -something...\n-vers\n...")

    data = {'version': 1}
    with open(correct, "w+") as file:
        yaml.dump(data, file)

    return config_path, default_config_path


mock_logging_config_data = {
    'handlers':
        {
            'mock_handler': {
                'filename': 'mock.log'
            }
        }
}


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

    @mock.patch('logging.config.dictConfig')
    def test_logger_running(self, mock_logging_config):

        with mock.patch('nephos.load_config.LOG') as mock_log:
            self.TestConfig.initialise()

            mock_logging_config.assert_called_with(mock.ANY)
            call_args, call_kwargs = mock_logging_config.call_args
            self.assertIsInstance(call_args[0], dict)

            expected_log_info = "** LOGGER CONFIGURED"
            mock_log.info.assert_called_with(expected_log_info)

    def test_load_data_correct_config_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config, default = create_mock_yaml(temp_dir)
            with mock.patch('nephos.load_config.__config_dir__', new=default), mock.patch(
                    'nephos.load_config.__default_config_dir__', new=default):
                call_return = self.TestConfig.load_data("test.yaml", True)
                self.assertIsInstance(call_return, dict)

    def test_load_data_correct_nonconfig_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config, default = create_mock_yaml(temp_dir)
            with mock.patch('nephos.load_config.__config_dir__', new=default), mock.patch(
                    'nephos.load_config.__default_config_dir__', new=default):
                file_path = os.path.join(default, "test.yaml")
                call_return = self.TestConfig.load_data(file_path, False)
                self.assertIsInstance(call_return, dict)

    def test_load_data_incorrect_config_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config, default = create_mock_yaml(temp_dir)
            with mock.patch('nephos.load_config.__config_dir__', new=config), mock.patch(
                    'nephos.load_config.__default_config_dir__', new=default):
                call_return = self.TestConfig.load_data("test.yaml", True)
                self.assertIsInstance(call_return, dict)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_load_data_incorrect_nonconfig_file(self, mock_out):
        with tempfile.TemporaryDirectory() as temp_dir:
            config, default = create_mock_yaml(temp_dir)
            with mock.patch('nephos.load_config.__config_dir__', new=config), mock.patch(
                    'nephos.load_config.__default_config_dir__', new=default):
                file_path = os.path.join(config, "test.yaml")
                call_return = self.TestConfig.load_data(file_path, False)
                output = mock_out.getvalue()
                expected_output = "Error in {file}:\n".format(file=file_path)
                self.assertIsNone(call_return)
                self.assertIn(expected_output, output)

    @mock.patch('nephos.load_config.__config_dir__')
    @mock.patch('nephos.load_config.__default_config_dir__')
    def test_load_data_nonexistent_config_file(self, mock_conf_dir, mock_def_conf_dir):
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_conf_dir.new, mock_def_conf_dir.new = create_mock_yaml(temp_dir)
            self.TestConfig.load_data("test", True)
            self.assertRaises(IOError)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_load_data_nonexistent_nonconfig_file(self, mock_out):
        with tempfile.TemporaryDirectory() as temp_dir:
            config, default = create_mock_yaml(temp_dir)
            with mock.patch('nephos.load_config.__config_dir__', new=config), mock.patch(
                    'nephos.load_config.__default_config_dir__', new=default):
                file_path = os.path.join(config, "test")
                self.TestConfig.load_data(file_path, False)
                output = mock_out.getvalue()
                expected_output = "Failed to open {file}".format(file=file_path)
                self.assertIn(expected_output, output)

    @mock.patch('nephos.load_config.Config.logging_config')
    def test_correct_log_path(self, config_data):
        config_data.__getitem__.side_effect = mock_logging_config_data.__getitem__
        config_data.__iter__.side_effect = mock_logging_config_data.__iter__
        name = self.TestConfig._correct_log_file_path('mock_handler')
        raw_name = pydash.get(mock_logging_config_data, 'handlers.mock_handler.filename')
        self.assertNotEqual(name, raw_name)
        full_name = os.path.join(__nephos_dir__, raw_name)
        self.assertEqual(name, full_name)

    @mock.patch('nephos.load_config.input')
    def test_load_mail_list(self, mock_input):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "email_test")

            # initially temp_file doesn't exist
            with mock.patch('nephos.load_config.CRITICAL_MAIL_ADDRS_PATH', new=temp_file):
                with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                    mock_input.return_value = "shivam.cs.iit.kgp@gmail.com shiv"
                    self.TestConfig.load_mail_list()
                    output = mock_out.getvalue()
                    expected_output = [
                        "No critical mail list file found!",
                        "Following emails removed from critical mail list due to wrong format!",
                        "['shiv']",
                        "You can add more critical mail recipients in {path}\n".format(path=temp_file)
                    ]
                    self.assertEqual(output, "\n".join(expected_output))

                # now temp_file exists
                with mock.patch('sys.stdout', new_callable=StringIO) as mock_out:
                    self.TestConfig.load_mail_list()
                    output = mock_out.getvalue()
                    expected_output = [
                        "Critical mail recipients loaded from {path}".format(path=temp_file),
                        "Following emails removed from critical mail list due to wrong format!",
                        "['shiv']",
                        "You can add more critical mail recipients in {path}\n".format(path=temp_file)
                    ]
                    self.assertEqual(output, "\n".join(expected_output))


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
