"""
Contains class for the checking of channel, whether online or not
"""
import os
import shutil
from logging import getLogger
from .checker import Checker
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
import pydash
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

        # TODO: Create a ChannelHandler class with list channels functions and call it in here
        # once the list if received, mock channel list below.
        self.channel_list = {
            "0": {
                "id": "abc123",
                "name": "channel_xyz",
                "ip": "host:port",
                "teltex_page": 34,
                "country": "nation_zyx",
                "languages": ["hello", "namaste", "salut"],
                "timezone": "IST",
                "status": "up"
            }
        }

        prev_stats = self._channel_stats()  # storing current stats as prev_stats for later comparison

        # create a list of IPs and pass it to recording
        ips = ["something@some", "something2@some2"]
        POOL.map(self._check_ip, ips)
        POOL.close()
        POOL.join()

        # TODO: grab new data and call _channel_stats
        # In case of change in the statistics, formulate report

        shutil.rmtree(self.TMP_PATH)

    def _check_ip(self, ip):
        """
        Evaluates whether an IP address is online or offline and updates it's status accordingly
        in the database.

        Parameters
        -------
        ip
            type: str
            ip address of the channel to be checked

        Returns
        -------

        """
        path = os.path.join(self.TMP_PATH, "test_{ip}.ts".format(ip=ip))
        record(ip, path, 5)
        if os.stat(path).st_size < MIN_BYTES:
            # TODO: make channel status down
            pass

    def _channel_stats(self):
        """
        A minimal function that returns the number of online and offline channels.
        # TODO: A full function to be developed for listing channels and their statistics.

        Returns
        -------
        stats
            type: dict
            number of channels down, down channel names, and up channels.

        """
        down_ch = 0
        up_ch = 0
        down_ch_names = []

        for key in self.channel_list:
            if pydash.get(self.channel_list, key+".status") == "down":
                down_ch += 1
                down_ch_names.append(pydash.get(self.channel_list, key+".name") + "@" +
                                     pydash.get(self.channel_list, key+".ip"))
            else:
                up_ch += 1
        stats = {"down_ch": down_ch, "down_ch_names": down_ch_names, "up_ch": up_ch}
        return stats


def record(ip_addr, addr, duration):
    """
    Function to record stream from the ip address for the given duration,
    and in the given addr.
    # TODO: to be moved to ChannelHandler

    Parameters
    ----------
    ip_addr
        type: str
        IP address of the stream, format "host:port"
    addr
        type: str
        address of the file path
    duration

    Returns
    -------

    """
    pass