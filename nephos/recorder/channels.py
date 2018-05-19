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
