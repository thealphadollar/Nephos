"""
Contains the main preprocess class
"""
import os
from logging import getLogger
from sqlite3 import Error
from multiprocessing import Pool, cpu_count, pool
from datetime import datetime
from . import get_preprocessor_config
from .methods import ApplyProcessMethods
from ..manage_db import DBHandler, DBException, TSK_ID_INDEX, \
    TSK_PATH_INDEX, TSK_STORE_INDEX, TSK_STAT_INDEX, TSK_FAIL_INDEX
from .. import __upload_dir__


LOG = getLogger(__name__)
POOL = Pool(processes=cpu_count())


class PreprocessHandler:
    """
    Class to init, load, add and process video streams
    """

    def __init__(self, scheduler):
        """
        Load settings and add preprocessing to scheduler.

        Parameters
        ----------
        scheduler
            type: Scheduler class
            default background job scheduler

        """
        self.config = get_preprocessor_config()
        self.scheduler = scheduler

    @staticmethod
    def init_preprocess_pipe():
        """
        Loads data from the database and passes it into the preprocessing pipe

        Returns
        -------

        """
        sql_command = 'SELECT * FROM tasks where status = "not processed"'
        # TODO: Test above command
        tasks_pool = []
        for task in PreprocessHandler._query_tasks(sql_command):
            tasks_pool.append((task[TSK_PATH_INDEX], task[TSK_STORE_INDEX]))

        if tasks_pool:
            try:
                POOL.starmap(ApplyProcessMethods, tasks_pool)
            except pool.MaybeEncodingError as _:
                pass

    # TODO: remove this
    @staticmethod
    def add_task():
        """
        this is for testing the preprocessor

        Returns
        -------

        """
        orig_path = input("Orig_path: ")
        ip_addr = input("IP_Addr: ")
        PreprocessHandler.insert_task(orig_path, ip_addr)

    @staticmethod
    def insert_task(orig_path, ip_addr):
        """
        Insert a new task into the "tasks" table

        Parameters
        -------
        orig_path
            type: str
            original path to the recorded file
        ip_addr
            type: str
            ip address of the channel of the recorded video

        Returns
        -------

        """
        try:
            with DBHandler.connect() as db_cur:
                ch_name = PreprocessHandler._get_channel_name(ip_addr, db_cur)
                store_path = os.path.join(__upload_dir__, ch_name + "_" + str(datetime.now().strftime("%Y-%m-%d-%H-%M")))
                lang, sub_lang = ApplyProcessMethods.get_lang(orig_path)

                data = {
                    "orig_path": orig_path,
                    "store_path": store_path,
                    "ch_name": ch_name,
                    "lang": lang,
                    "sub_lang": sub_lang
                }

                task_id = DBHandler.insert_data(db_cur, "tasks", data)
                if task_id is not None:
                    LOG.debug("Task (id = %s) added with following data:\n%s", task_id, data)

        except DBException as err:
            LOG.warning("Failed to insert task for recording: %s", orig_path)
            LOG.debug(err)

    @staticmethod
    def display_tasks():
        """
        Prints the list of pending tasks

        Returns
        -------

        """
        sql_command = "SELECT * FROM tasks"
        tasks = PreprocessHandler._query_tasks(sql_command)

        LOG.info("\nID\tStatus\t\tFail Count\tFile")
        for task in tasks:
            to_print_data = [
                task[TSK_ID_INDEX],
                task[TSK_STAT_INDEX],
                task[TSK_FAIL_INDEX],
                "\t"+task[TSK_PATH_INDEX]
            ]
            print("\t".join(str(x) for x in to_print_data))

    @staticmethod
    def rm_task():
        """
        Removes a task from the task list on user command.
        This is to be used mostly in case of excessive failures

        Returns
        -------

        """
        task_id = input("Task ID: ").lower()
        sql_command = "DELETE FROM tasks WHERE task_id=?"
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(sql_command, (task_id, ))
                LOG.info("Task (ID=%s) removed from database", task_id)
        except Error as err:
            LOG.warning("Failed to remove task!")
            LOG.debug(err)

    def add_to_scheduler(self):
        """
        Adds preprocessing job to class' scheduler.

        Returns
        -------

        """
        jobs = ["run_preprocessor"]
        job_funcs = {
            "run_preprocessor": self.init_preprocess_pipe,
        }

        for job in jobs:
            LOG.debug("Adding %s default job to scheduler...", job)
            self.scheduler.add_necessary_jobs(job_funcs[job], job,
                                              self.config['interval'])

    @staticmethod
    def _query_tasks(sql_cmd):
        """
        Queries the tasks table using the given command

        Parameters
        -------
        sql_cmd
            type: str
            sql command to be queried

        Returns
        -------

        """
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(sql_cmd)
                return db_cur.fetchall()
        except DBException as err:
            LOG.warning("Failed to query tasks table!")
            LOG.debug(err)

    @staticmethod
    def _get_channel_name(ip_addr, db_cur):
        """

        Parameters
        ----------
        ip_addr
            type: str
            ip address of a channel
        db_cur
            type: sqlite database cursor
            cursor to the database of channels

        Returns
        -------
            type: str
            name of the channel to which the ip address belongs

        """
        sql_command = "SELECT name FROM channels WHERE ip=?"
        db_cur.execute(sql_command, (ip_addr,))
        return db_cur.fetchall()[0][0]
