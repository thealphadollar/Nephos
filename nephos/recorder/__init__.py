"""
Stores all the code concerning the stream recorder
"""
from ..load_config import Config


def recorder_config():
    """
    Loads and returns the configuration for the recording module

    Returns
    -------

    """
    modules_config = Config.load_data('modules.yaml', True)
    return modules_config['recording']
