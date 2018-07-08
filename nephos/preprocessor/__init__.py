"""
Stores all the code concerning the preprocessor operations
"""
from ..load_config import Config


config = None


# Below function is deprecated at the moment
def set_preprocessor_config(preprocess_config):
    """
    sets config for the module

    Parameters
    ----------
    preprocess_config
        type: dict
        configuration for the preprocessor

    Returns
    -------

    """
    global config
    config = preprocess_config


def get_preprocessor_config():
    """
    Returns
    -------
    type: dict
    configuration for the preprocessing module

    """
    global config
    config = Config.load_data("modules.yaml", True)['preprocess']
    return config
