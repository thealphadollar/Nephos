"""
Contains class for the checking of channel, whether online or not
"""
import os
import shutil
from logging import getLogger
from multiprocessing.pool import ThreadPool
from itertools import repeat
from multiprocessing import cpu_count
from .checker import Checker
from ..manage_db import DBHandler, CH_IP_INDEX, CH_NAME_INDEX, CH_STAT_INDEX
from ..recorder.channels import ChannelHandler
from ..custom_exceptions import DBException
from .. import __nephos_dir__

LOG = getLogger(__name__)
POOL = ThreadPool(cpu_count())
MIN_BYTES = 10 * 1024  # 10 KBs, recording created in 5 seconds should be larger than this


class ChannelOnlineCheck(Checker):
    """
    Checks whether all the channels are online or not and
    prepares a report of the number of channels up, down and
    the magnitude of change.
    """

    def _execute(self):
        """
        executes the test for online channel check

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
        self.TMP_PATH = os.path.join(__nephos_dir__, self._get_data("channel_online_check", "path"))
        os.makedirs(self.TMP_PATH, exist_ok=True)

        self.channel_list = ChannelHandler.grab_ch_list()

        prev_stats = self._channel_stats()  # current stats as prev_stats for later comparison

        # create a list of IPs and pass it to recording
        ips = self._extract_ips()
        try:
            with DBHandler.connect() as db_cur:
                POOL.starmap(self._check_ip, zip(repeat(db_cur), ips))
                POOL.close()
                POOL.join()
        except DBException as err:
            LOG.warning("Couldn't update channel status")
            LOG.debug("%s", err)

        self.channel_list = ChannelHandler.grab_ch_list()
        new_stats = self._channel_stats()

        # formulate report
        report = self._formulate_report(prev_stats, new_stats)
        self._handle(report[0], report[1])

        LOG.info("Channel online check maintenance finished")
        shutil.rmtree(self.TMP_PATH)
        LOG.info("tmp directory removed")

    def _check_ip(self, db_cur, ip):
        """
        Evaluates whether an IP address is online or offline and updates it's status accordingly
        in the database.

        Parameters
        -------
        db_cur
            sqlite database cursor
        ip
            type: str
            ip address of the channel to be checked

        Returns
        -------

        """
        path = os.path.join(self.TMP_PATH, "test_{ip}.ts".format(ip=ip))
        ChannelHandler.record(ip, path, 5)
        if os.stat(path).st_size < MIN_BYTES:
            command = """UPDATE channels
                            SET status = "down"
                            WHERE ip = ? 
                        """
            db_cur.execute(command, tuple(ip))
            LOG.debug("Channel with ip: %s down", ip)

    def _channel_stats(self):
        """
        A minimal function that returns the number of online and offline channels.

        Returns
        -------
        stats
            type: dict
            number of channels down, down channel names, and up channels.

        """
        down_ch = 0
        up_ch = 0
        down_ch_names = []

        for _ in self.channel_list:
            if self.channel_list[CH_STAT_INDEX] == "down":
                down_ch += 1
                down_ch_names.append(self.channel_list[CH_NAME_INDEX] + "@" +
                                     self.channel_list[CH_IP_INDEX])
            else:
                up_ch += 1
        stats = {"down_ch": down_ch, "down_ch_names": down_ch_names, "up_ch": up_ch}
        return stats

    def _extract_ips(self):
        """
        extracts the list of ip of all channels

        Returns
        -------
        type: list
        list of ips of all channels

        """
        ips = []
        for _ in self.channel_list:
            ips.append(self.channel_list[CH_IP_INDEX])

        return ips

    @staticmethod
    def _formulate_report(prev_stats, new_stats):
        """
        Frames a report based on the channel online tests

        Parameters
        ----------
        prev_stats
            type: dict
            status of the channels before current maintenance run
        new_stats
            type: dict
            status of the channels after current run

        Returns
        -------
            type: tuple
                type: bool
                True if critical, False otherwise
                type: str
                Message

        """
        if set(prev_stats["down_ch_names"]) == set(new_stats["down_ch_names"]):
            msg = "No channel in the status of channels"
            report = (False, msg)
            return report

        msg = [
            "Current stats:\nFollowing {number} channels are down:".format(number=new_stats["down_ch"]),
            ", ".join(new_stats["down_ch_names"]),
            "\nPreviously:",
            ", ".join(prev_stats["down_ch_names"])

        ]
        report = (True, msg)
        return report
