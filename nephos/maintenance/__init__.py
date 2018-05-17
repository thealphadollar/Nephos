"""
This directory stores the maintenance jobs for various nephos modules.

To add a new job, create a new file with the job code and add it to the maintenance class present below.
"""
from logging import getLogger


log = getLogger(__name__)


class NephosMaintenance:
    """
    Manages all the maintenance tasks in a nut shell.
    """

    def __init__(self, config):
        # add space check functions
        pass

    def run_disk_space_check(self):
        pass

    def run_channel_online_check(self):
        pass

    def run_auth_uploader_check(self):
        pass

