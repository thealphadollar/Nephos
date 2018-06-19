"""
Manages all operations related to channels, including adding, deleting and updating channel data
"""
from logging import getLogger
from sqlite3 import Error
import subprocess
import os
from datetime import datetime
from . import get_recorder_config
from ..manage_db import DBHandler
from ..exceptions import DBException
from .. import __recording_dir__, __upload_dir__
from .. import validate_entries
from ..preprocessor.preprocess import PreprocessHandler

LOG = getLogger(__name__)


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
        with DBHandler.connect() as db_cur:
            self.insert_channels(db_cur, validate_entries("channel", ch_data))

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
    def insert_channels(db_cur, ch_data):
        """
        Adds channels to the database

        Parameters
        ----------
        db_cur
            sqlite cursor to the database
        ch_data
            type: dict
            dict of channels' data to be appended to the channel table

        Returns
        -------

        """
        for key in ch_data.keys():
            ch_id = DBHandler.insert_data(db_cur, "channels", ch_data[key])
            if ch_id is not None:
                LOG.info("Channel (id = %s) added with following data:\n%s", ch_id, ch_data[key])

                # create directory for channel recordings and putting processed files
                ch_dir = os.path.join(__recording_dir__, ch_data[key]["name"])
                processed_ch_dir = os.path.join(__upload_dir__, ch_data[key]["name"])
                os.makedirs(ch_dir, exist_ok=True)
                os.makedirs(processed_ch_dir, exist_ok=True)

    @staticmethod
    def delete_channel():
        """
        Deletes channel from the database

        Returns
        -------

        """
        ch_ip_name = input("Channel name or ip: ").lower()
        command = "DELETE FROM channels WHERE name=? OR ip=?"
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(command, (ch_ip_name, ch_ip_name))
                LOG.info("Channel with name/ip = %s removed from database", ch_ip_name)
        except Error as err:
            LOG.warning("Failed to remove channel!")
            LOG.debug(err)

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
                db_cur.execute("SELECT * FROM channels")
                return db_cur.fetchall()
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
            if not _is_up(ip_addr):
                return False

        config = get_recorder_config()

        duration_27khz = int(duration_secs * 27000000)
        timeout_str = '-d {:d}'.format(duration_27khz)
        path_to_multicat = config['path_to_multicat']
        ifaddr = config['ifaddr']
        if ifaddr:
            ifaddr = '/ifaddr=' + ifaddr

        cmd = "{multicat_path} {duration} -u @{channel_ip}{ifaddr} {out_file}".format(
            multicat_path=path_to_multicat, duration=timeout_str, channel_ip=ip_addr,
            ifaddr=ifaddr, out_file=addr)
        try:
            record_process = subprocess.Popen(cmd,
                                              shell=True,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT)
            process_output, _ = record_process.communicate()
            LOG.debug(process_output)
            PreprocessHandler.insert_task(addr, ip_addr)
            return True
        except (OSError, subprocess.CalledProcessError) as err:
            LOG.warning("Recording for channel with ip %s, failed!", ip_addr)
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
    command = """SELECT status FROM channels WHERE ip=?"""
    with DBHandler.connect() as db_cur:
        db_cur.execute(command, (ip_addr, ))
        status = db_cur.fetchall()
    if status[0][0] == "up":
        return True
    return False
