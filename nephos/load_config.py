from . import __nephos_dir__, __config_dir__, __default_config_dir__
import os
import logging
import logging.config
import yaml
import yaml.error
import pydash


log = logging.getLogger(__name__)


class Config:
    """
    class managing all the configuration work
    """
    nephos_config = None
    recorder_config = None
    preprocess_config = None
    uploader_config = None

    def load_config(self):
        """
        Loads configurations from /config/ (Path relative to __nephos_dir__)

        Returns
        -------

        """

        nephos_config_path = os.path.join(__config_dir__, "nephos.yaml")
        recorder_config_path = os.path.join(__config_dir__, "recorder.yaml")
        preprocess_config_path = os.path.join(__config_dir__, "preprocess.yaml")
        uploader_config_path = os.path.join(__config_dir__, "uploader.yaml")

        # loading configuration
        self.nephos_config = self._load_config_data(nephos_config_path,
                                                    os.path.join(__default_config_dir__, "nephos.yaml"))
        self.recorder_config = self._load_config_data(recorder_config_path,
                                                      os.path.join(__default_config_dir__, "recorder.yaml"))
        self.preprocess_config = self._load_config_data(preprocess_config_path,
                                                        os.path.join(__default_config_dir__, "preprocess.yaml"))
        self.uploader_config = self._load_config_data(uploader_config_path,
                                                      os.path.join(__default_config_dir__, "uploader.yaml"))

        # updating configuration as needed with manual data / environment variables
        config_update = list(self._config_update())
        pydash.merge(self.nephos_config, config_update[0])
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
        logging.config.dictConfig(self.nephos_config['log'])
        log.info("* LOGGER READY")

    @staticmethod
    def _load_config_data(path, default_path):
        """
        Loads data from YAML configuration

        Using PyYAML's safe_load method
        Read more at https://security.openstack.org/guidelines/dg_avoid-dangerous-input-parsing-libraries.html

        Parameters
        ----------
        path
            type: str
            Path to the configuration file
        default_path
            type: str
            Path to the default configuration file

        Returns
        -------
        dict
            Dictionary containing configuration information provided by the path or default path

        """
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
        data_point = "log.handlers.{name}.filename".format(name=handler_name)
        return os.path.join(__nephos_dir__, pydash.get(self.nephos_config, data_point))

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
        nephos_config_update = {
            'log':
                {
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
        }
        recorder_config_update = {

        }
        preprocess_config_update = {

        }
        uploader_config_update = {

        }
        # TODO: Find a better method than this nesting

        config_list = [nephos_config_update, recorder_config_update, preprocess_config_update, uploader_config_update]
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
    if len(name) == 0:
        print("Warning: Environment variable {env_name} not set! Some functions might not work properly!")
    return env_value
