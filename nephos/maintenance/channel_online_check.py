"""
Contains class for the checking of channel, whether online or not
"""
import os
from tempfile import TemporaryDirectory
from logging import getLogger
from multiprocessing import pool, cpu_count
from functools import partial
from .checker import Checker
from ..manage_db import DBHandler, CH_IP_INDEX, CH_NAME_INDEX, CH_STAT_INDEX
from ..recorder.channels import ChannelHandler
from ..exceptions import DBException

LOG = getLogger(__name__)
POOL = pool.ThreadPool(cpu_count())
MIN_BYTES = 1024  # 1 KB, recording created in 5 seconds should be larger than this
CH_DOWN_COMMAND = """UPDATE channels
                    SET status = "down"
                    WHERE ip = ?"""
CH_UP_COMMAND = """UPDATE channels
                    SET status = "up"
                    WHERE ip = ?"""


class ChannelOnlineCheck(Checker):
    """
    Checks whether all the channels are online or not and
    prepares a report of the number of channels up, down and
    the magnitude of change.
    """

    def __init__(self, config_maintain):

        Checker.__init__(self, config_maintain)
        self.channel_list = None

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

        with TemporaryDirectory() as tmpdir:
            LOG.debug("Channel online check started, tmp directory %s created", tmpdir)

            self.channel_list = ChannelHandler.grab_ch_list()

            prev_stats = self._channel_stats()  # current stats as prev_stats for later comparison

            # create a list of IPs and pass it to recording
            ips = self._extract_ips()
            if ips:  # when ip is not empty
                try:
                    with DBHandler.connect() as db_cur:
                        POOL.map(partial(self._check_ip, db_cur=db_cur, path=tmpdir), ips)
                except DBException as err:
                    LOG.warning("Couldn't update channel status")
                    LOG.debug(err)

                self.channel_list = ChannelHandler.grab_ch_list()
                new_stats = self._channel_stats()

                # formulate report
                report = self._formulate_report(prev_stats, new_stats)
                self._handle(report[0], report[1])
            else:
                LOG.warning("No channels found!")

        LOG.debug("tmp directory removed")

    @staticmethod
    def _check_ip(ip_addr, db_cur, path):
        """
        Evaluates whether an IP address is online or offline and updates it's status accordingly
        in the database.

        Parameters
        -------
        ip_addr
            type: str
            ip address of the channel to be checked
        db_cur
            sqlite database cursor
        path
            type: dir
            temporary directory to be used for channel checking

        Returns
        -------

        """
        path = os.path.join(path, "test_{ip}.ts".format(ip=ip_addr))
        is_down = False
        if ChannelHandler.record_stream(ip_addr, path, 5, test=True):
            try:
                if os.stat(path).st_size < MIN_BYTES:
                    is_down = True
                    LOG.debug("Channel with ip: %s down", ip_addr)
            except FileNotFoundError:
                is_down = True
                LOG.debug("Failed to bind to multicat; wrong channel address")
        else:
            is_down = True
            LOG.debug("IP:%s check failed", ip_addr)

        if is_down:
            db_cur.execute(CH_DOWN_COMMAND, (ip_addr,))
            LOG.debug("IP:%s is down", ip_addr)
        else:
            db_cur.execute(CH_UP_COMMAND, (ip_addr,))
            LOG.debug("IP:%s is up", ip_addr)

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

        for channel in self.channel_list:
            if channel[CH_STAT_INDEX] == "down":
                down_ch += 1
                down_ch_names.append(channel[CH_NAME_INDEX] + "::" +
                                     channel[CH_IP_INDEX])
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
        for channel in self.channel_list:
            ips.append(channel[CH_IP_INDEX])

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
            msg = "No new down channels!"
            report = (False, msg)
            return report

        msg = [
            "\nCurrent stats:\nFollowing {number} channel(s) are down:".format(
                number=new_stats["down_ch"]),
            ", ".join(new_stats["down_ch_names"]),
            "Previously:",
            ", ".join(prev_stats["down_ch_names"])

        ]
        report = (True, "\n".join(msg))
        return report
