"""
Stores all the code concerning the stream recorder
"""
config = None


def set_uploader_config(uploader_config):
    """
    sets config for the module

    Parameters
    ----------
    uploader_config
        type: dict
        configuration for the recorder

    Returns
    -------

    """
    global config
    config = uploader_config


def get_uploader_config():
    """
    Returns
    -------
    type: dict
    configuration for the uploading module

    """
    global config
    return config
