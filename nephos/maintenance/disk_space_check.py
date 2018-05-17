"""
Define DiskSpaceCheck class and it's required functions
"""

import shutil
from logging import getLogger
from .. import __nephos_dir__
from .checker import Checker

LOG = getLogger(__name__)


class DiskSpaceCheck(Checker):
    """
    To check if the disk space is less than a minimum threshold defined in config file
    """

    def _execute(self):
        """
        executes the test for disk space

        Returns
        -------
        Passes the following parameters to _handle()
            critical_flag
                type: bool
                True when critical condition met, False otherwise
            result_msg
                type: str
                message that is to be logged

        """
        job_type = "disk_space_check"
        min_free_bytes = self._gb_to_bytes(self._get_data(job_type, "min_space"))
        min_percent = self._get_data(job_type, "min_percent")

        total, _, free = shutil.disk_usage(__nephos_dir__)  # provides data in bytes
        result_msg = [""]
        critical_flag = False  # flag is true if error is critical

        # evaluate for free space left
        if free < min_free_bytes:
            result_msg.append("Low Disk Space: The free space on disk is less from "
                              "minimum required space by {diff:0.2f} GBs".format(
                                  diff=self._bytes_to_gbs(min_free_bytes - free)))
            critical_flag = True
        else:
            result_msg.append("Disk Space: The free space on disk is {value:0.2f} GBs".format(
                value=self._bytes_to_gbs(free)))

        # evaluate for free space percentage
        if ((free/total) * 100) < min_percent:
            result_msg.append("Low Free Disk Percentage: The free space percentage on "
                              "the disk is low at {current:0.2f} than suggested minimum "
                              "of {required:0.2f}!".format(current=((free/total) * 100),
                                                           required=min_percent))
            critical_flag = True
        else:
            result_msg.append("Free Disk Percentage:  The free space on disk is {value:0.2f}%"
                              .format(value=((free/total) * 100)))

        self._handle(critical_flag, "\n".join(result_msg))

    @staticmethod
    def _gb_to_bytes(in_gbs):
        """
        Converts value in GBs to bytes

        Parameters
        ----------
        in_gbs
            type: float
            value in gigabytes

        Returns
        -------
            type: float
            value in bytes

        """
        return int(in_gbs) * 1024 * 1024 * 1024

    @staticmethod
    def _bytes_to_gbs(in_bytes):
        """
        Converts value in bytes to GBs

        Parameters
        ----------
        in_bytes
            type: float
            value in bytes

        Returns
        -------
            type: float
            value in GBs
        """
        return int(in_bytes) / (1024 * 1024 * 1024)
