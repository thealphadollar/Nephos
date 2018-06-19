"""
Defines maintenance class and it's functioning
"""

# This directory stores the maintenance jobs for various nephos modules.
# To add a new job, create the job's python code file and add it to the maintenance class.

from logging import getLogger
import pydash
from .disk_space_check import DiskSpaceCheck
from .channel_online_check import ChannelOnlineCheck
from ..load_config import Config


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

        self.disk_checker = DiskSpaceCheck(self.config)
        self.channel_checker = ChannelOnlineCheck(self.config)

    def add_maintenance_to_scheduler(self, scheduler):
        """
        adds all maintenance jobs to scheduler

        Parameters
        ----------
        scheduler
            type: Scheduler class
            to add maintenance jobs into

        Returns
        -------

        """
        # TODO: Add more jobs
        jobs = ["disk_space_check", "channel_online_check"]
        job_funcs = {
            "disk_space_check": self.call_disk_space_check,
            "channel_online_check": self.call_channel_online_check
        }

        for job in jobs:
            LOG.debug("Adding %s maintenance job to scheduler...", job)
            scheduler.add_necessary_jobs(job_funcs[job], job,
                                         self._get_maintenance_data(job))

    @staticmethod
    def call_disk_space_check():
        """
        Calls disk space check job passing the kind.
        It may or may not execute depending on the setting.

        Returns
        -------

        """
        DiskSpaceCheck(_refresh_config()).to_run("disk_space_check")

    @staticmethod
    def call_channel_online_check():
        """
        Calls channel online check job passing the kind.
        It may or may not execute depending on the setting.

        Returns
        -------

        """
        ChannelOnlineCheck(_refresh_config()).to_run("channel_online_check")

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

    def _get_maintenance_data(self, job):
        """
        loads particular value from the maintenance dictionary

        Parameters
        ----------
        job
            type: str
            name of the job

        Returns
        -------
        type: int
        repeating interval of the job
        """
        return pydash.get(self.config, "jobs.{job}.interval".format(job=job))


def _refresh_config():
    """
    Refreshes the loaded configuration for the jobs to enable/disable
    during runtime.

    Returns
    -------
    type: dict
    configuration for the maintenance job

    """
    config = Config()
    config.load_config()
    config = config.maintenance_config
    return config
