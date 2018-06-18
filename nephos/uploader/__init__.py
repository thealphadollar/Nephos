"""
Stores all the code concerning the uploader
"""

config = None


def set_uploader_config(uploader_config):
    """
    sets config for the module

    Parameters
    ----------
    uploader_config
        type: dict
        configuration for the uploader

    Returns
    -------

    """
    global config
    config = uploader_config
