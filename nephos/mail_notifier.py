"""
Contains functions for sending reports and critical log entries to the system administrator
"""
import os
import subprocess
from datetime import datetime
from logging import getLogger

from . import load_mail_list, __nephos_dir__


LOG = getLogger(__name__)
REPORT_FILE = os.path.join(__nephos_dir__, ".report")


def send_mail(msg, msg_type):
    """
    Sends mail to the email addresses present in CRITICAL_MAIL_ADDRS_PATH

    Parameters
    -------
    msg
        type: str
        string to be send as message
    msg_type
        type: str
        defines the type and decides the subject for the mail

    Returns
    -------
    type: bool
    true if mail was send, false otherwise
    """
    emails = load_mail_list()

    if msg_type != "report":
        msg = str(datetime.now().strftime("[%d/%m/%Y %I:%M:%S %p]: ")) + msg

    subject = {
        "ch_down": "[NEPHOS] New Channels Down",
        "critical_disk": "[NEPHOS] Disk Space Critically Low",
        "corrupt_file": "[NEPHOS] Corrupt Recording",
        "report": "[NEPHOS] Daily Report",
        "critical": "[NEPHOS] Critical Notification",
        "update_failed": "[NEPHOS] Updating Config Failed",
        "update_success": "[NEPHOS] Updating Config Successful"
    }

    cmd = 'echo "{msg}" | mail -s "{subject}" {emails}'.format(
        msg=msg,
        subject=subject[msg_type],
        emails=emails
    )

    try:
        LOG.debug("running '%s' command", cmd)
        record_process = subprocess.Popen(cmd,
                                          shell=True,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT)
        process_output, _ = record_process.communicate()
        LOG.debug(process_output)
        return True
    except subprocess.CalledProcessError as err:
        LOG.warning("Sending notification mail failed!")
        LOG.debug(err)
        return False


def add_to_report(msg):
    """
    Append string to the EOF of the report file.

    Parameters
    ----------
    msg
        type: str
        message to be appended to the report file.

    Returns
    -------

    """
    msg = str(datetime.now().strftime("[%m/%d/%Y %I:%M:%S %p]: ")) + msg + "\n"
    with open(REPORT_FILE, "a") as report_file:
        report_file.write(msg)


def send_report():
    """
    Reads data from report file, converts it to str message and calls send mail on it.

    Returns
    -------

    """
    with open(REPORT_FILE, "r") as report_file:
        msg = report_file.read()
    send_mail(msg, "report")
    os.remove(REPORT_FILE)
