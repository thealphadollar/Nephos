"""
Manages all operations related to channels, including adding, deleting and updating channel data
"""
from logging import getLogger
from sqlite3 import Error
import click
import subprocess
import os
from datetime import datetime
from ..manage_db import DBHandler
from ..custom_exceptions import DBException
from .. import __recording_dir__

LOG = getLogger(__name__)


class ChannelHandler:
    """
    Class unifying all channel concerned methods
    """

    @click.command()
    @click.option("--name", prompt="Channel name", help="name of the channel")
    @click.option("--ip", prompt="IP", help="ip address of the channel")
    @click.option("--country", prompt="Country codes [separated by space]",
                  help="country codes for the channel")
    @click.option("--lang", prompt="Language codes [separated by space]",
                  help="available languages in the channel")
    @click.option("--tmz", prompt="Timezone", help="timezone of the channel")
    def add_channel(self, name, ip, country, lang, tmz):
        """
        Provides CLI to add a single channel

        Parameters
        -------
        explained in the click options

        Returns
        -------
        channel_id
            type: int
            the unique id for the channel

        """
        ch_data = {
            0: {
                "name": name,
                "ip": ip,
                "country_code": country,
                "lang": lang,
                "timezone": tmz
            }
        }
        with DBHandler.connect() as db_cur:
            self.insert_channels(db_cur, ch_data)

    def display_channel(self):
        """
        Displays list of channels currently stored in the database

        Returns
        -------

        """
        channels = self.grab_ch_list()
        LOG.info("id\tname\tip\tcountry\tlanguage\ttimezone\tstatus")
        for channel in channels:
            LOG.info("\t".join(str(x) for x in channel))

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
        for channel in ch_data:
            ch_id = DBHandler.insert_data(db_cur, "channels", channel)
            LOG.info("New channel (id = %s) added with following data:\n%s", ch_id, channel)
            # create directory for channel recordings
            ch_dir = os.path.join(__recording_dir__, channel["name"])
            os.makedirs(ch_dir, exist_ok=True)

    @staticmethod
    def delete_channels(ch_ip_name):
        """
        Deletes channel from the database

        Parameters
        ----------
        ch_ip_name
            type: str
            channel' IP or name

        Returns
        -------

        """
        command = "DELETE FROM channels WHERE name=? OR ip=?"
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(command, (ch_ip_name, ch_ip_name))
                LOG.info("Channel with name/ip = %s removed from database", ch_ip_name)
        except Error as err:
            LOG.warning("Failed to remove channel!")
            LOG.error(err)

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
            LOG.error(err)

    @staticmethod
    def record(ip_addr, addr, duration_secs):
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

        Returns
        -------

        """
        if not _is_up(ip_addr):
            return

        duration_27khz = int(duration_secs * 27000000)
        timeout_str = '-d {:d}'.format(duration_27khz)
        addr = addr + str(datetime.now().strftime("%Y-%m-%d_%H%M") + ".ts")

        cmd = "multicat {duration} -u @{channel_ip} {out_file}".format(
            duration=timeout_str, channel_ip=ip_addr, out_file=addr)
        try:
            subprocess.check_call(cmd, shell=False)
        except subprocess.CalledProcessError as err:
            LOG.warning("Recording for channel with ip %s", ip_addr)
            LOG.error(err)


def _is_up(ip):
    """
    Queries if the channel was up in the previous test.

    Returns
    -------
        type: bool
        True, if the channel was up, False otherwise.

    """
    command = """SELECT status FROM channels WHERE ip=?"""
    with DBHandler.connect() as db_cur:
        status = db_cur.execute(command, ip)

    if status == "up":
        return True
    return False
