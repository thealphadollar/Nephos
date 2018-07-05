"""
Contains the uploader abstract base class.
All uploading clients should be derived class Uploader and implement the necessary methods.
"""
from abc import ABC, abstractmethod
import ntpath
import shutil
from functools import partial
from logging import getLogger
from multiprocessing import pool, cpu_count
from ..manage_db import DBHandler, DBException, TSK_STORE_INDEX, TSK_SHR_INDEX
from . import get_uploader_config

LOG = getLogger(__name__)
CMD_GET_FOLDERS = 'SELECT * FROM tasks WHERE status = "processed"'
CMD_SET_UPLOADING = """UPDATE tasks
                    SET status = "uploading"
                    WHERE store_path = ?"""
CMD_RM_TASK = """DELETE
                FROM tasks
                WHERE store_path = ?"""
POOL = pool.ThreadPool(cpu_count())


class Uploader(ABC):

    def __init__(self, scheduler):
        self._config = get_uploader_config()
        self._scheduler = scheduler
        self.service = None  # uploading client service
        self.auth()

        self._add_to_scheduler()

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
    def begin_uploads(client, up_func):
        """
        Parse folders to be uploaded from the database

        Parameters
        -------
        client
            the authenticated client to be used for uploading folders.
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
        except DBException as error:
            LOG.warning("Failed to connect to database")
            LOG.debug(error)
            return

        upload_pool = []
        for task in tasks_list:
            upload_pool.append((task[TSK_STORE_INDEX], task[TSK_SHR_INDEX]))

        if upload_pool:
            POOL.starmap(partial(up_func, client=client), upload_pool)

    @staticmethod
    @abstractmethod
    def _upload(service, folder, share_list):
        """
        Uploads the folder and appends share entities

        Parameters
        -------
        service
            uploading client of the cloud platform
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

    def _add_to_scheduler(self):
        """
        Adds uploading job to class' scheduler.

        Returns
        -------

        """
        jobs = ["run_uploader"]
        job_funcs = {
            "run_uploader": self.begin_uploads,
        }

        args = [self._get_upload_service(), self._upload]

        for job in jobs:
            LOG.debug("Adding %s default job to scheduler...", job)
            self._scheduler.add_cron_necessary_job(job_funcs[job], job, self._config['start_time'],
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
