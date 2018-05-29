"""
File containing initialising functions for Nephos

Used to store attributes which will be used throughout the program.
"""
import os
from distutils.dir_util import copy_tree  # pylint: disable=no-name-in-module,import-error
import re
import click


__home_dir__ = os.path.expanduser('~')
# path of the directory where __init__.py is
__package_dir__ = os.path.dirname(os.path.realpath(__file__))

__nephos_dir__ = os.path.join(__home_dir__, "Nephos")
__config_dir__ = os.path.join(__nephos_dir__, "config")
__log_dir__ = os.path.join(__nephos_dir__, "logs")
__db_dir__ = os.path.join(__nephos_dir__, "databases")
__recording_dir__ = os.path.join(__nephos_dir__, "recordings")
__upload_dir__ = os.path.join(__nephos_dir__, "processed")
__docs_dir__ = os.path.join(__nephos_dir__, "docs")

__default_config_dir__ = os.path.join(__package_dir__, "default_config")
__default_docs_dir__ = os.path.join(__package_dir__, "../docs")

REGEX_CHECK = {
    "email": re.compile(r"[^@\s][\w\d\._\+][^\s]+@[\w\d\.]+\.[\w\d]*"),
    "ip": re.compile(r"[^\s]+:[\d]+"),
    "country_code": re.compile(r"[a-zA-Z ]+"),
    "language": re.compile(r"[a-zA-Z ]+"),
    "timezone": re.compile(r"[a-zA-Z ]+"),
    "start_time": re.compile(r"\d{2}:\d{2}"),
    "duration": re.compile(r"\d+"),
    "repetition": re.compile(r"[01]{7}")
}


def validate_entries(data_type, data):
    """
    Validates the data entry for the channels, jobs and sharelists

    Parameters
    ----------
    data_type
        type: str
        information about whether it's channel, job or share entity
    data
        type: dict
        contains multiple channels' data

    Returns
    -------
    type: dict
    validated and rectified data

    """

    for key in data.keys():
        name = key

        def correct(dict_key):
            """
            Ask user to correct the value for the key

            Parameters
            ----------
            dict_key
                type: str
                dict key value to alter

            Returns
            -------

            """
            data[key][dict_key] = input("Enter correct {key} for {type} {name}: ".format(
                key=dict_key,
                type=data_type,
                name=name
            ))

        for key2 in data[key].keys():
            if key2 in REGEX_CHECK.keys():
                # separate check for emails since they are clustered with space between them
                if key2 == "email":
                    for email in data[key][key2]:
                        if not REGEX_CHECK[key2].match(email):
                            click.echo("{email} incorrect".format(email=email))
                            correct(key2)
                else:
                    if not REGEX_CHECK[key2].match(data[key][key2]):
                        correct(key2)

    return data


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
        return False

    # make directories
    os.makedirs(__nephos_dir__)
    os.makedirs(__config_dir__)
    os.makedirs(__log_dir__)
    os.makedirs(__db_dir__)
    os.makedirs(__recording_dir__)
    os.makedirs(__upload_dir__)
    os.makedirs(__docs_dir__)

    # copy default configuration to the __config_dir__
    copy_tree(__default_config_dir__, __config_dir__)
    copy_tree(__default_docs_dir__, __docs_dir__)

    return True


if __name__ == '__main__':
    pass
