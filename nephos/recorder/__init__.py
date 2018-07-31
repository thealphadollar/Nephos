"""
Stores all the code concerning the stream recorder
"""
CONFIG = None


def set_recorder_config(recorder_config):
    """
    sets CONFIG for the module

    Parameters
    ----------
    recorder_config
        type: dict
        configuration for the recorder

    Returns
    -------

    """
    global CONFIG
    CONFIG = recorder_config


def get_recorder_config():
    """
    Returns
    -------
    type: dict
    configuration for the recording module

    """
    global CONFIG
    return CONFIG
