"""
File containing initialising functions for Nephos

Used to store attributes which will be used throughout the program.
"""
import os
from distutils.dir_util import copy_tree  # pylint: disable=no-name-in-module,import-error


__home_dir__ = os.path.expanduser('~')
# path of the directory where __init__.py is
__package_dir__ = os.path.dirname(os.path.realpath(__file__))

__nephos_dir__ = os.path.join(__home_dir__, "Nephos")
__config_dir__ = os.path.join(__nephos_dir__, "config")
__log_dir__ = os.path.join(__nephos_dir__, "logs")
__db_dir__ = os.path.join(__nephos_dir__, "databases")
__recording_dir__ = os.path.join(__nephos_dir__, "recordings")
__upload_dir__ = os.path.join(__nephos_dir__, "processed")

__default_config_dir__ = os.path.join(__package_dir__, "default_config")


def first_time():
    """
    If the program is being run first time, create the directory Nephos
    and it's subdirectories in user's home directory

    -Nephos:
        - config: contains user editable configuration files
        - logs: store log information in txt
        - databases: stores the database for Nephos
        - recordings: stores the recorded streams
        - processed: stores processed mp4 files to be uploaded

    Returns
    -------
    bool: True, when Nephos launched first time
          False,  otherwise

    """

    if os.path.exists(__nephos_dir__):
        # TODO: Remove copying from this nest when all configurations are written
        # copy default configuration to the __config_dir__
        copy_tree(__default_config_dir__, __config_dir__)
        return False

    # make directories
    os.makedirs(__nephos_dir__)
    os.makedirs(__config_dir__)
    os.makedirs(__log_dir__)
    os.makedirs(__db_dir__)
    os.makedirs(__recording_dir__)
    os.makedirs(__upload_dir__)

    # copy default configuration to the __config_dir__
    copy_tree(__default_config_dir__, __config_dir__)

    return True


if __name__ == '__main__':
    pass
