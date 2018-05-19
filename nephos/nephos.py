"""
The pipeline for the working of nephos
"""
from abc import ABC
from logging import getLogger
from .custom_exceptions import DBException
from .load_config import Config
from .manage_db import DBHandler
from .recorder.channels import ChannelHandler

LOG = getLogger(__name__)


class Nephos(ABC):
    """
    The abstract base class from which new derived classes can be created to support varying
    online storage platforms.

    """

    def __init__(self):
        pass

    @staticmethod
    def load_data(data_file):
        """
        loads data from a file which contains both channels and share entities
        Segregates them based on the dictionary key and then passes the dictionary to
        appropriate functions in recorder and uploader.

        Parameters
        -------
        data_file
            type: str
            path to the data file

        Returns
        -------

        """
        data = Config.load_data(data_file)
        try:
            with DBHandler.connect() as db_cur:
                ChannelHandler.insert_channels(db_cur, data["channels"])
                # TODO: Function to manage share_lists
        except DBException as err:
            LOG.warning("Data addition failed")
            LOG.error(err)
