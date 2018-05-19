"""
Contains class which facilitates loading configurations files and implementing them
"""

import os
import logging
import logging.config
import yaml
import yaml.error
import pydash
from . import __nephos_dir__, __config_dir__, __default_config_dir__


LOG = logging.getLogger(__name__)


class Config:
    """
    class managing all the configuration work
    """
    logging_config = None
    maintenance_config = None
    recorder_config = None
    preprocess_config = None
    uploader_config = None

    def load_config(self):
        """
        Loads configurations from /config/ (Path relative to __nephos_dir__)

        Returns
        -------

        """

        # loading configuration
        self.logging_config = self.load_data("logging.yaml")
        self.maintenance_config = self.load_data("maintenance.yaml")
        self.recorder_config = self.load_data("recorder.yaml")
        self.preprocess_config = self.load_data("preprocess.yaml")
        self.uploader_config = self.load_data("uploader.yaml")

        # updating configuration as needed with manual data / environment variables
        config_update = list(self._config_update())
        pydash.merge(self.logging_config, config_update[0])
        pydash.merge(self.recorder_config, config_update[1])
        pydash.merge(self.preprocess_config, config_update[2])
        pydash.merge(self.uploader_config, config_update[3])

    def initialise(self):
        """
        Initialises logger, database etc. with loaded configuration
        Returns
        -------

        """
        # Initialise logger
        logging.config.dictConfig(self.logging_config)
        LOG.info("** LOGGER CONFIGURED")

    @staticmethod
    def load_data(file_name):
        """
        Loads data from YAML configuration

        Using PyYAML's safe_load method, read more at
        https://security.openstack.org/guidelines/dg_avoid-dangerous-input-parsing-libraries.html

        Parameters
        ----------
        file_name
            type: str
            name of the config file

        Returns
        -------
        type: dict
        Dictionary containing configuration information provided by the path or default path

        """
        path = os.path.join(__config_dir__, file_name)
        default_path = os.path.join(__default_config_dir__, file_name)
        try:
            with open(path, 'r') as config_file:
                yaml_data = config_file.read()
                return yaml.safe_load(yaml_data)
        except yaml.error.YAMLError as exception:
            print("YAMLError in {file}:\n".format(file=path) + str(exception))
            print("using default configuration for {file}".format(file=path))
            with open(default_path) as config_file:
                yaml_data = config_file.read()
                return yaml.safe_load(yaml_data)

    def _correct_log_file_path(self, handler_name):
        """
        Appends relative file path specified for the handler's file in filename to __nephos_dir__
        Parameters
        ----------
        handler_name
            type: str
            name of the handler (eg. "nephos_file")

        Returns
        -------
            type: str
            absolute path to the log file for the handle

        """
        data_point = "handlers.{name}.filename".format(name=handler_name)
        return os.path.join(__nephos_dir__, pydash.get(self.logging_config, data_point))

    def _config_update(self):
        """
        Overrides/Updates data present in the configuration files

        Environment variables used:
            CRED_MAIL:
                type: str
                stores the mail address of the sender
            CRED_PASS:
                type: str
                stores the password for the email address
            MAIL_HOST:
                type: str
                stores the host address for the mail SMTP server
            MAIL_PORT:
                type: int
                stores the port address for the mail SMTP server

        Returns
        -------
            type: list
            A list containing dictionaries with updated/new data

        """
        # manual update of configuration data
        logging_config_update = {
            'handlers':
                {
                    'nephos_file':
                        {
                            'filename': self._correct_log_file_path('nephos_file')
                        },
                    'recorder_file':
                        {
                            'filename': self._correct_log_file_path('recorder_file')
                        },
                    'preprocess_file':
                        {
                            'filename': self._correct_log_file_path('preprocess_file')
                        },
                    'uploader_file':
                        {
                            'filename': self._correct_log_file_path('uploader_file')
                        },
                    'email':
                        {
                            'credentials': (get_env_var('CRED_EMAIL'), get_env_var('CRED_PASS')),
                            'mailhost': (get_env_var('MAIL_HOST'), get_env_var('MAIL_PORT')),
                            'secure': ()
                        }
                }
        }
        recorder_config_update = {

        }
        preprocess_config_update = {

        }
        uploader_config_update = {

        }
        # TODO: Find a better method than this nesting

        config_list = [logging_config_update, recorder_config_update,
                       preprocess_config_update, uploader_config_update]
        return config_list


def get_env_var(name):
    """
    Gets environment variable from the OS
    Issues a warning if the environment variable is not fount.

    Parameters
    ----------
    name
        type:str
        name of the environment variable

    Returns
    -------
        type: depends on environment variable
        data of the environment variable

    """
    env_value = os.getenv(name)

    if not name:  # if no env variable set for the same
        print("Warning: Environment variable {env_name} not set! "
              "Some functions might not work properly!")
    return env_value
