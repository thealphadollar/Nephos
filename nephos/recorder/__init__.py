"""
Stores all the code concerning the stream recorder
"""
config = None


def set_recorder_config(recorder_config):
    """
    sets config for the module

    Parameters
    ----------
    recorder_config
        type: dict
        configuration for the recorder

    Returns
    -------

    """
    global config
    config = recorder_config


def get_recorder_config():
    """
    Returns
    -------
    type: dict
    configuration for the recording module

    """
    global config
    return config
