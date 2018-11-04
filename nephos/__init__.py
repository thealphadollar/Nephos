"""
File containing initialising functions for Nephos

Used to store attributes which will be used throughout the program.
"""
import os
from distutils.dir_util import copy_tree  # pylint: disable=no-name-in-module,import-error
import re
import logging


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
__default_db_dir__ = os.path.join(__package_dir__, "databases")


LOG = logging.getLogger(__name__)
REGEX_CHECK = {
    "email": re.compile(r"[^@\s][\w\d\._\+][^\s]+@[\w\d\.]+\.[\w\d]*"),
    "ip": re.compile(r"[^\s]+:[\d]+"),
    "country_code": re.compile(r"[a-zA-Z ]+"),
    "language": re.compile(r"[a-zA-Z ]+"),
    "timezone": re.compile(r"[a-zA-Z ]+"),
    "start_time": re.compile(r"\d{2}:\d{2}"),
    "duration": re.compile(r"[^0]\d*"),
    "repetition": re.compile(r"[01]{7}")
}
# path to store the list of critical mail recipients
CRITICAL_MAIL_ADDRS_PATH = os.path.join(__nephos_dir__, ".critical_mail_addrs")


def load_mail_list():
    """
    Checks and removes incorrect mail addresses from toaddr parameter
    of logger's SMTP handler

    Returns
    -------
    type: list
    updated list of emails

    """

    if os.path.exists(CRITICAL_MAIL_ADDRS_PATH):
        # print("Critical mail recipients loaded from", CRITICAL_MAIL_ADDRS_PATH)
        with open(CRITICAL_MAIL_ADDRS_PATH, "r") as file:
            raw_data = file.read()
    else:
        print("No critical mail list file found!")
        raw_data = input("Enter email address(es) separated by single whitespace:\n")
        with open(CRITICAL_MAIL_ADDRS_PATH, "w+") as file:
            file.write(raw_data)

    emails = [str(email) for email in raw_data.split(" ")]

    removed = []
    for email in emails:
        if not REGEX_CHECK["email"].match(email):
            removed.append(email)
            emails.remove(email)

    if removed:
        print("Following emails removed from critical mail list due to wrong format!")
        print(removed)

    # print("You can add more critical mail recipients in", CRITICAL_MAIL_ADDRS_PATH)
    return ",".join(emails)


def validate_entries(data):
    """
    Validates the data entry for the channels, jobs and sharelists

    Parameters
    ----------
    data
        type: dict
        contains multiple channels' data

    Returns
    -------
    type: dict
    validated and rectified data

    """

    for key in data.copy().keys():
        removed = False

        for key2 in data[key].keys():
            if key2 in REGEX_CHECK.keys():
                # separate check for emails since they are clustered with space between them
                if key2 == "email":
                    for email in data[key][key2].split(' '):
                        if not REGEX_CHECK[key2].match(email):
                            print("{email} incorrect".format(email=email))
                            data.pop(key, None)
                            removed = True
                            break
                else:
                    if not REGEX_CHECK[key2].match('{}'.format(data[key][key2])):
                        data.pop(key, None)
                        removed = True
            if removed:
                break

    return data


def first_time():
    """
    If the program is being run first time, create the directory Nephos
    and its subdirectories in user's home directory

    -Nephos:
        - config: contains user editable configuration files
        - logs: store log information in txt
        - databases: stores the database for Nephos
        - recordings: stores the recorded streams
        - processed: stores processed mp4 files to be uploaded
        - docs: stores the detailed documentation for Nephos

    Returns
    -------
    bool: True, when Nephos launched first time
          False, otherwise

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
    copy_tree(__default_db_dir__, __db_dir__)
    copy_tree(__default_docs_dir__, __docs_dir__)

    load_mail_list()

    return True


if __name__ == '__main__':
    pass
