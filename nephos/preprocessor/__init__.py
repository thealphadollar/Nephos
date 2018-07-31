"""
Stores all the code concerning the preprocessor operations
"""
from ..load_config import Config


CONFIG = None


# Below function is deprecated at the moment
def set_preprocessor_config(preprocess_config):
    """
    sets CONFIG for the module

    Parameters
    ----------
    preprocess_config
        type: dict
        configuration for the preprocessor

    Returns
    -------

    """
    global CONFIG
    CONFIG = preprocess_config


def get_preprocessor_config():
    """
    Returns
    -------
    type: dict
    configuration for the preprocessing module

    """
    global CONFIG
    CONFIG = Config.load_data("modules.yaml", True)['preprocess']
    return CONFIG
