"""
Defines maintenance class and it's functioning
"""

# This directory stores the maintenance jobs for various nephos modules.
# To add a new job, create the job's python code file and add it to the maintenance class.

from logging import getLogger
from smtplib import SMTPException
import pydash
from .disk_space_check import DiskSpaceCheck


LOG = getLogger(__name__)


class Maintenance:
    """
    Manages all the maintenance tasks in a nut shell.
    """

    def __init__(self, maintenance_config):
        """
        Initiate the Maintenance object with it's configuration

        Parameters
        ----------
        maintenance_config
            type: dictionary
            maintenance configuration from "maintenance.yaml"

        """
        self.config = maintenance_config

        # add space check functions
        self.disk_checker = DiskSpaceCheck(self.config)

    def run_disk_space_check(self):
        """
        Runs disk space check job and passes the evaluation result to _handle function

        Returns
        -------

        """
        if self._to_execute("disk_space_check"):
            is_critical, msg = self.disk_checker.run()
            self._handle(is_critical, msg)

    def run_channel_online_check(self):
        """
        Runs channel on-air test and passes the evaluation result to _handle function

        Returns
        -------

        """
        pass

    def run_auth_uploader_check(self):
        """
        Runs authorisation test for uploading and passes the evaluation result to _handle function

        Returns
        -------

        """
        pass

    @staticmethod
    def _handle(is_critical, msg):
        """
        Handles the evaluation results of the maintenance jobs
        Uses,
            LOG.critical for sending error mail
            LOG.info for displaying information regarding exceptions
            LOG.debug for writing detailed error report to nephos.txt logs

        Parameters
        ----------
        is_critical
            type: bool
            True if the issue is critical, False otherwise
        msg
            type: str
            message to be logged

        Returns
        -------

        """
        if is_critical:

            # below line sends an email and catches exception if any
            try:
                LOG.critical(msg)
            except SMTPException as error:
                LOG.warning("Sending mail failed due to SMTPException! For details "
                            "please check nephos.txt logs")
                LOG.debug(error)

        else:
            LOG.info(msg)

    def _to_execute(self, job):
        """
        Checks from config file if the maintenance job is to be executed

        Parameters
        -------
        job
            type: str
            kind of the job to be executed

        Returns
        -------
        type: bool
        True if the job enabled, False otherwise
        """
        data_point = "jobs.{job_name}.enabled".format(job_name=job)

        if pydash.get(self.config, data_point):
            return True

        return False
