"""
Stores all the code concerning the stream recorder
"""
CONFIG = None


def set_uploader_config(uploader_config):
    """
    sets CONFIG for the module

    Parameters
    ----------
    uploader_config
        type: dict
        configuration for the recorder

    Returns
    -------

    """
    global CONFIG
    CONFIG = uploader_config


def get_uploader_config():
    """
    Returns
    -------
    type: dict
    configuration for the uploading module

    """
    global CONFIG
    return CONFIG
