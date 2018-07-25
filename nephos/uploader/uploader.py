"""
Contains the uploader abstract base class.
All uploading clients should be derived class Uploader and implement the necessary methods.
"""
from abc import ABC, abstractmethod
import ntpath
import shutil
import sqlite3
from logging import getLogger
from ..manage_db import DBHandler, DBException
from . import get_uploader_config
from .FTP import FTPUploader

LOG = getLogger(__name__)
CMD_GET_FOLDERS = 'SELECT * FROM tasks WHERE status = "processed"'
CMD_SET_UPLOADING = """UPDATE tasks
                    SET status = "uploading"
                    WHERE store_path = ?"""
CMD_RM_TASK = """DELETE
                FROM tasks
                WHERE store_path = ?"""


class Uploader(ABC):

    def __init__(self, scheduler):
        self._config = get_uploader_config()
        self._scheduler = scheduler
        self.service = None  # uploading client service
        self.auth()

    @staticmethod
    @abstractmethod
    def auth():
        """
        Authorise the module.

        Returns
        -------

        """
        pass

    @staticmethod
    @abstractmethod
    def _get_upload_service():
        """
        Returns
        -------
        upload_client
            the authenticated client to be used for uploading folders.

        """
        pass

    @staticmethod
    def begin_uploads(up_func):
        """
        Parse folders to be uploaded from the database

        Parameters
        -------
        up_func
            type: callable
            upload function to be called

        Returns
        -------

        """
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(CMD_GET_FOLDERS)
                tasks_list = db_cur.fetchall()
        except (DBException, sqlite3.OperationalError) as error:
            LOG.warning("Failed to connect to database")
            LOG.debug(error)
            return

        if tasks_list:
            LOG.info("Uploading to FTP server first...")
            FTPUploader(tasks_list)
            LOG.info("Beginning upload to cloud storage...")
            up_func(tasks_list)

    @staticmethod
    @abstractmethod
    def _upload(tasks_list):
        """
        Uploads the folder and appends share entities

        Parameters
        -------
        tasks_list
            type:  list
            list containing details of recordings to be uploaded.

        Returns
        -------

        """
        # make sure to add a function to upload logs to a remote folder in cloud
        pass

    @staticmethod
    def _set_uploading(folder):
        """
        Sets the status of the entry with corresponding folder to "uploading"

        Parameters
        ----------
        folder
            type: str
            path to the folder being uploaded

        Returns
        -------

        """
        with DBHandler.connect() as db_cur:
            db_cur.execute(CMD_SET_UPLOADING, (folder, ))

    @staticmethod
    def _remove(folder):
        """
        Removes the corresponding folder and it's entry from tasks table post-upload.

        Parameters
        ----------
        folder
            type: str
            path to the storage of post processed files

        Returns
        -------

        """
        with DBHandler.connect() as db_cur:
            db_cur.execute(CMD_RM_TASK, (folder, ))

        shutil.rmtree(folder)

    def add_to_scheduler(self):
        """
        Adds uploading job to class' scheduler.

        Returns
        -------

        """
        jobs = ["run_uploader"]
        job_funcs = {
            "run_uploader": self.begin_uploads,
        }

        args = [self._upload]

        for job in jobs:
            LOG.debug("Adding %s default job to scheduler...", job)
            timings = self._config['timings']
            for key in timings:
                self._scheduler.add_cron_necessary_job(job_funcs[job], job+"@"+timings[key], timings[key],
                                                       self._config['repetition'], args)

    @staticmethod
    def _get_name(path):
        """
        Parses name from the absolute path.

        Parameters
        ----------
        path
            type: str
            absolute path to the file

        Returns
        ---------
            type: str
            name of the folder or file with extension
        -------

        """
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)  # return tail when file, otherwise other one for folder
