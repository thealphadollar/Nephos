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
        str to be send as message
    msg_type
        type: str
        defines the type and decides the subject for the mail

    Returns
    -------
    type: bool
    true if sending was successful, false otherwise
    """
    emails = load_mail_list()

    if msg_type != "report":
        msg = str(datetime.now().strftime("[%m/%d/%Y %I:%M:%S %p]: ")) + msg

    if msg_type == "ch_down":
        subject = "[NEPHOS] New Channels Down"
    elif msg_type == "critical_disk":
        subject = "[NEPHOS] Disk Space Critically Low"
    elif msg_type == "corrupt_file":
        subject = "[NEPHOS] Corrupt Recording"
    elif msg_type == "report":
        subject = "[NEPHOS] Daily Report"
    elif msg_type == "critical":
        subject = "[NEPHOS] Critical Notification"

    cmd = 'echo "{msg}" | mail -s "{subject}" {emails}'.format(
        msg=msg,
        subject=subject,
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
    Append string to the EOF of report file.

    Parameters
    ----------
    msg
        type: str
        message to be appended to the report's file.

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
