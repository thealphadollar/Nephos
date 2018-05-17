"""
Defines maintenance class and it's functioning
"""

# This directory stores the maintenance jobs for various nephos modules.
# To add a new job, create the job's python code file and add it to the maintenance class.

from logging import getLogger
from .disk_space_check import DiskSpaceCheck
from .channel_online_check import ChannelOnlineCheck


LOG = getLogger(__name__)


class Maintenance:
    """
    Manages all the maintenance tasks in a nut shell.
    """

    def __init__(self, maintenance_config):
        """
        Initiate the Maintenance object with it's configuration.
        All jobs have different call methods for ease of scheduling.

        Parameters
        ----------
        maintenance_config
            type: dictionary
            maintenance configuration from "maintenance.yaml"

        """
        self.config = maintenance_config

        # add space check functions
        self.disk_checker = DiskSpaceCheck(self.config)
        self.channel_checker = ChannelOnlineCheck(self.config)

    def call_disk_space_check(self):
        """
        Calls disk space check job passing the kind.
        It may or may not execute depending on the setting.

        Returns
        -------

        """
        self.disk_checker.to_run("disk_space_check")

    def call_channel_online_check(self):
        """
        Calls channel online check job passing the kind.
        It may or may not execute depending on the setting.

        Returns
        -------

        """
        self.channel_checker.to_run("channel_online_check")

    def call_uploader_auth_check(self):
        """
        Calls uploader auth check job passing the kind.
        It may or may not execute depending on the setting.

        Returns
        -------

        """
        pass

    def call_file_upload_check(self):
        """
        Calls disk space check job passing the kind.
        It may or may not execute depending on the setting.

        Returns
        -------

        """
        pass
