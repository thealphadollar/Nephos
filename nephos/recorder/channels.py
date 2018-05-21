"""
Manages all operations related to channels, including adding, deleting and updating channel data
"""
from logging import getLogger
from ..manage_db import DBHandler

LOG = getLogger(__name__)


class ChannelHandler:
    """
    Class unifying all channel concerned methods
    """

    @staticmethod
    def add_channel():
        """
        Provides CLI to add a single channel

        Returns
        -------
        channel_id
            type: int
            the unique id for the channel

        """
        # TODO: Complete this
        pass

    @staticmethod
    def insert_channels(db_cur, ch_data_list):
        """
        Adds a single channel to the database

        Parameters
        ----------
        db_cur
            cursor to the database
        ch_data_list
            type: list
            list of channels' data to be appended to the channel table

        Returns
        -------
        channel_id
            type: int
            the unique id for the created channel

        """
        for ch_data in ch_data_list:
            DBHandler.insert_data(db_cur, "channels", tuple(ch_data))

    @staticmethod
    def list_channels():
        """
        Extracts the table of currently added channels

        Returns
        -------
        type: dict
        dictionary containing key-value pairs for all the channels

        """
        pass

    @staticmethod
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
