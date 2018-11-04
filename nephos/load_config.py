"""
Contains class which facilitates loading configurations files and implements them
"""

import os
import logging
from logging import getLogger
import logging.config
import yaml
import yaml.error
import pydash

from . import __nephos_dir__, __config_dir__, __default_config_dir__
from .recorder import set_recorder_config
from .uploader import set_uploader_config


LOG = getLogger(__name__)


class Config:
    """
    class managing all the configuration work
    """
    logging_config = None
    maintenance_config = None
    modules_config = None

    def load_config(self):
        """
        Loads configurations from /config/ (Path relative to __nephos_dir__)

        Returns
        -------

        """

        # loading configuration
        self.logging_config = self.load_data("logging.yaml", True)
        self.maintenance_config = self.load_data("maintenance.yaml", True)
        self.modules_config = self.load_data("modules.yaml", True)

        # updating configuration as needed with manual data / environment variables
        config_update = list(self._config_update())
        pydash.merge(self.logging_config, config_update[0])
        pydash.merge(self.modules_config, config_update[1])

    def initialise(self):
        """
        Initializes logger, database etc. with loaded configuration
        Returns
        -------

        """
        # Initialize logger
        logging.config.dictConfig(self.logging_config)
        LOG.info("** LOGGER CONFIGURED")

    def configure_modules(self):
        """
        Loads configuration into each module

        Returns
        -------

        """
        set_recorder_config(self.modules_config['recording'])
        # set_preprocessor_config(self.modules_config['preprocess'])
        set_uploader_config(self.modules_config['upload'])
        LOG.info('Modules configured')

    @staticmethod
    def load_data(file_name, is_config):
        """
        Loads data from YAML configuration

        Using PyYAML's safe_load method, read more at
        https://security.openstack.org/guidelines/dg_avoid-dangerous-input-parsing-libraries.html

        Parameters
        ----------
        file_name
            type: str
            name of the config file, else full path for data files
        is_config
            type: bool
            if file is config, default loads.

        Returns
        -------
        type: dict
        Dictionary containing configuration information provided by the path or default path
        type: bool
        False if the file is a data file and fails to load

        """
        if is_config:
            path = os.path.join(__config_dir__, file_name)
        else:
            path = file_name
        default_path = os.path.join(__default_config_dir__, file_name)

        try:
            try:
                with open(path, 'r') as config_file:
                    yaml_data = config_file.read()
                    return yaml.safe_load(yaml_data)
            except IOError as err:
                print("Failed to open", path)
                LOG.debug(err)
                raise yaml.error.YAMLError

        except yaml.error.YAMLError as exception:
            print("Error in {file}:\n".format(file=path))
            print(exception)
            if is_config:
                print("using default configuration for {file}".format(file=path))
                with open(default_path) as config_file:
                    yaml_data = config_file.read()
                    return yaml.safe_load(yaml_data)
            else:
                return False

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
        # extensive nesting method has been used for better readability
        logging_config_update = {
            'handlers':
                {
                    'nephos_file':
                        {
                            'filename': self._correct_log_file_path('nephos_file')
                        }
                }
        }
        # TODO: below dict not needed
        modules_config_update = {

        }

        config_list = [logging_config_update, modules_config_update]
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

    if not env_value:  # if no env variable set for the same
        print("Warning: Environment variable {env_name} not set! "
              "Some functions might not work properly!".format(env_name=name))
    return env_value
