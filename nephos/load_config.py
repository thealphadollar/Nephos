from . import __nephos_dir__, __config_dir__, __default_config_dir__
import os
import logging
import logging.config
import yaml
import yaml.error
import pydash


log = logging.getLogger(__name__)


def load_config_data(path, default_path):
    """
    Loads data from YAML configuration file
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
            return yaml.load(yaml_data)
    except yaml.error.__all__ as exception:
        print("YAMLError in {file}:\n".format(file=path) + str(exception))
        print("using default configuration for {file}".format(file=path))
        with open(default_path) as config_file:
            yaml_data = config_file.read()
            return yaml.load(yaml_data)


def load_config():
    """
    Handles all the general configuration related to Nephos and it's modules.
    Loads configurations from /config/

    Environment variables used:
        TODO: Add environment variables for sensitive data

    Returns
    -------

    """

    nephos_config_path = os.path.join(__config_dir__, "nephos.yaml")
    recorder_config_path = os.path.join(__config_dir__, "recorder.yaml")
    preprocess_config_path = os.path.join(__config_dir__, "preprocess.yaml")
    uploader_config_path = os.path.join(__config_dir__, "uploader.yaml")

    nephos_config = load_config_data(nephos_config_path, os.path.join(__default_config_dir__, "nephos.yaml"))
    recorder_config = load_config_data(recorder_config_path, os.path.join(__default_config_dir__, "recorder.yaml"))
    preprocess_config = load_config_data(preprocess_config_path, os.path.join(__default_config_dir__, "preprocess.yaml"))
    uploader_config = load_config_data(uploader_config_path, os.path.join(__default_config_dir__, "uploader.yaml"))

    # manual update of configuration data
    log_file = os.path.join(__nephos_dir__, pydash.get(nephos_config, 'log.handlers.file.filename'))
    nephos_config_update = {
        'log':
            {
                'handlers':
                    {
                        'file':
                            {
                                'filename': log_file
                            },
                        'email':
                            {
                                'credentials': ('codestashkgp@gmail.com', 'pass')
                            }
                    }
            }
    }  # TODO: Find a better method than this nesting

    pydash.merge(nephos_config, nephos_config_update)

    # Initialise logger with default configuration
    logging.config.dictConfig(nephos_config['log'])

    log.info("* LOGGER READY")
