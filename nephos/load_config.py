from . import __nephos_dir__, __config_dir__
import os
import logging
import logging.config
import yaml
import pydash


log = logging.getLogger(__name__)


def load_config_data(path):
    """
    Loads data from YAML configuration file
    Parameters
    ----------
    path
        type: str
        Path to the configuration file

    Returns
    -------

    """
    with open(path, 'w+') as config_file:
        yaml_data = config_file.read()
        return yaml.load(yaml_data)


def load_config():
    """
    Handles all the general configuration related to Nephos and it's modules.
    Loads configurations from /config/

    Environment variables used:
        TODO: Add environment variables

    Returns
    -------

    """

    nephos_config_path = os.path.join(__config_dir__, "nephos.yaml")
    # recorder_config_path = os.path.join(__config_dir__, "recorder.yaml")
    # preprocess_config_path = os.path.join(__config_dir__, "preprocess.yaml")
    # uploader_config_path = os.path.join(__config_dir__, "uploader.yaml")

    nephos_config = load_config_data(nephos_config_path)
    # recorder_config = load_config_data(recorder_config_path)
    # preprocess_config = load_config_data(preprocess_config_path)
    # uploader_config = load_config_data(uploader_config_path)

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
                                'credentials': ('codestashkgp@gmail.com', 'BroCodeKGP')
                            }
                    }
            }
    }

    pydash.merge(nephos_config, nephos_config_update)

    # Initialise logger with default configuration
    logging.config.dictConfig(nephos_config['log'])
    log.debug("debug")
    log.info("information")
    log.error("error")
    log.warning("warning")
    log.critical("critical")
