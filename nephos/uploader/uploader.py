"""
Contains the uploader abstract base class.
All uploading clients should be derived class Uploader and implement the necessary methods.
"""
from abc import ABC, abstractmethod
from logging import getLogger
from multiprocessing import Pool, cpu_count
from ..manage_db import DBHandler, DBException
from . import get_uploader_config

LOG = getLogger(__name__)


class Uploader(ABC):

    def __init__(self):
        self.config = get_uploader_config()

    @abstractmethod
    def auth(self):
        """
        Authorise the module.

        Returns
        -------

        """
        pass

    def begin_uploads(self):
        """
        Parse folders to be uploaded from the database
        Returns
        -------

        """

    def grab_share_list(self):
        """
        Queries the share lists database and matches the tags associated with the current file
        Returns
        -------

        """

    @staticmethod
    @abstractmethod
    def _upload(client, folder, share_list):
        """
        Uploads the folder.

        Parameters
        -------
        client
            uploading client from the cloud platform
        folder
            type: str
            path to folder to be uploaded
        share_list
            type: list
            list of entities the file is to be shared with

        Returns
        -------

        """
        pass
