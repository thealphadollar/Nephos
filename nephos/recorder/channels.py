"""
Manages all operations related to channels, including adding, deleting and updating channel data
"""
import os
import subprocess
from logging import getLogger
from sqlite3 import Error
from datetime import datetime

from . import get_recorder_config
from .. import __recording_dir__, validate_entries
from ..manage_db import DBHandler, CH_STAT_INDEX
from ..exceptions import DBException
from ..preprocessor.preprocess import PreprocessHandler
from ..mail_notifier import add_to_report


LOG = getLogger(__name__)
CMD_GET_CHANNELS = "SELECT * FROM channels"
MIN_BYTES = 1024  # 1 KB, recording created in 5 seconds should be larger than this


class ChannelHandler:
    """
    Class unifying all channel concerned methods
    """

    def add_channel(self):
        """
        Provides CLI to add a single channel

        Returns
        -------
        channel_id
            type: int
            the unique id for the channel

        """
        name = input("Channel name: ").lower()
        ip_addr = str(input("IP address [e.g. 0.0.0.0:8080]: "))
        country = input("Country codes [separated by space]: ").lower()
        lang = input("Language codes [separated by space]: ").lower()
        tmz = input("Timezone: ").lower()

        ch_data = {
            0: {
                "name": name,
                "ip": ip_addr,
                "country_code": country,
                "lang": lang,
                "timezone": tmz
            }
        }
        self.insert_channels(ch_data)

    def display_channel(self):
        """
        Displays list of channels currently stored in the database

        Returns
        -------

        """
        channels = self.grab_ch_list()
        LOG.info("\nid\tname\tip\t\t\tcountry\tlang\ttmz\tstatus")
        for channel in channels:
            print("\t".join(str(x) for x in channel))

    @staticmethod
    def insert_channels(ch_data):
        """
        Adds channels to the database

        Parameters
        ----------
        ch_data
            type: dict
            dict of channels' data to be appended to the channel table

        Returns
        -------

        """
        ch_data = validate_entries(ch_data)
        for key in ch_data.keys():
            ch_data[key]["name"] = "_".join(
                ch_data[key]["name"].lower().split()
            )  # replace whitespace with underscore
            with DBHandler.connect() as db_cur:
                ch_id = DBHandler.insert_data(db_cur, "channels", ch_data[key])
            if ch_id is not None:
                LOG.info("Channel (id = %s) added with following data:\n%s", ch_id, ch_data[key])

                # create directory for channel recordings and putting processed files
                ch_dir = os.path.join(__recording_dir__, ch_data[key]["name"])
                os.makedirs(ch_dir, exist_ok=True)

    @staticmethod
    def delete_channel():
        """
        Deletes channel from the database

        Returns
        -------

        """
        command = "DELETE FROM channels"
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(command)
            LOG.info("All channels removed from database")
        except Error as err:
            LOG.warning("Failed to remove channels!")
            LOG.debug(err)
            raise IOError

    @staticmethod
    def grab_ch_list():
        """
        Extracts the table of currently stored channels

        Returns
        -------
        type: tuple
        tuple containing column values for all the channels

        """
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(CMD_GET_CHANNELS)
                channels = db_cur.fetchall()
            return channels
        except DBException as err:
            LOG.warning("Failed to get channel list.")
            LOG.debug(err)

    @staticmethod
    def record_stream(ip_addr, addr, duration_secs, test=False):
        """
        Function to record stream from the ip address for the given duration,
        and in the given addr.

        Parameters
        ----------
        ip_addr
            type: str
            IP address of the stream, format "host:port"
        addr
            type: str
            absolute file path, without ".ts", to save the recording
        duration_secs
            type: int
            duration to record the show in seconds
        test
            type: bool
            True if run by channel online check test, False otherwise

        Returns
        -------
        type: bool
        True if successful, False otherwise

        """
        if not test:
            addr = addr + str(datetime.now().strftime("%Y-%m-%d_%H%M") + ".ts")
            aux_addr = str.replace(addr, ".ts", ".aux")
            if not _is_up(ip_addr):
                add_to_report("Recording IP:{ip_addr} skipped since the channel is down.".format(
                    ip_addr=ip_addr
                ))
                return False

        config = get_recorder_config()

        duration_27khz = int(duration_secs * 27000000)
        timeout_str = '-d {:d}'.format(duration_27khz)
        path_to_multicat = config['path_to_multicat']
        ifaddr = config['ifaddr']
        if ifaddr:
            ifaddr = '/ifaddr=' + ifaddr

        cmd = "{multicat_path} {duration} -u @{channel_ip}{ifaddr} '{out_file}'".format(
            multicat_path=path_to_multicat, duration=timeout_str, channel_ip=ip_addr,
            ifaddr=ifaddr, out_file=addr)
        try:
            LOG.debug("running '%s' command", cmd)
            record_process = subprocess.Popen(cmd,
                                              shell=True,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT)
            process_output, _ = record_process.communicate()
            LOG.debug(process_output)
            if not test:
                os.remove(aux_addr)
                if os.stat(addr).st_size <= MIN_BYTES:
                    os.remove(addr)
                else:
                    PreprocessHandler.insert_task(addr, ip_addr)
            return True
        except (OSError, subprocess.CalledProcessError) as err:
            LOG.warning("Recording for channel with ip %s, failed!", ip_addr)
            add_to_report("Recording IP:{ip_addr} failed due to following error:\n{error}\n".format(
                ip_addr=ip_addr,
                error=err
            ))
            LOG.debug(err)
            return False


def _is_up(ip_addr):
    """
    Queries if the channel was up in the previous test.

    Parameters
    -------
    ip_addr
        type: str
        ip address of the queried channel

    Returns
    -------
        type: bool
        True, if the channel was up, False otherwise.

    """
    command = """SELECT * FROM channels WHERE ip=?"""
    with DBHandler.connect() as db_cur:
        db_cur.execute(command, (ip_addr, ))
        ch_data = db_cur.fetchall()[0]
    if ch_data[CH_STAT_INDEX] == "up":
        return True
    return False
