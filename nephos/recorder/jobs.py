"""
Stores all code related to recording jobs
"""

import os
from logging import getLogger
from ..manage_db import DBHandler
from ..custom_exceptions import DBException
from ..load_config import Config
from .. import __recording_dir__
from .. import validate_entries

LOG = getLogger(__name__)


class JobHandler:
    """
    Handles addition of jobs
    """

    def __init__(self, scheduler):
        """
        initiates the JobHandler with the Scheduler class

        Parameters
        ----------
        scheduler
            type: Scheduler
            currently active Scheduler class from scheduler module
        """
        self._scheduler = scheduler

    def add_job(self):
        """
        Provides CLI for a single job addition and then calls insert_jobs with the data

        Returns
        -------

        """
        # accepting inputs
        name = input("Job name: ").lower()
        channel_name = input("Channel name: ").lower()
        start_time = input("Start time [HH:MM]: ")
        duration = int(input("Duration [in minutes]: "))
        rep = input("Run on [eg. 1010000 for sunday and tuesday]: ")
        job_data = {
            0: {
                "name": name,
                "channel_name": channel_name,
                "start_time": start_time,
                "duration": duration,
                "repetition": rep
            }
        }
        try:
            with DBHandler.connect() as db_cur:
                self.insert_jobs(db_cur, validate_entries("job", job_data))
        except DBException as err:
            LOG.warning("Data addition failed")
            LOG.error(err)

    def load_jobs(self):
        """
        loads data from a file which contains jobs
        Segregates them based on the dictionary key and then passes the dictionary to
        appropriate functions in JobHandler.

        Returns
        -------

        """
        # path to the data file
        data_file = input("File path: ")

        data = Config.load_data(data_file, False)
        try:
            with DBHandler.connect() as db_cur:
                self.insert_jobs(db_cur, data)
        except DBException as err:
            LOG.warning("Data addition failed")
            LOG.error(err)

    def insert_jobs(self, db_cur, job_data):
        """
        passes job data to add_recording_job method of Scheduler class.
        Parameters
        ----------
        db_cur
            type: sqlite database cursor
            cursor to the database of channels
        job_data
            type: dict
            dict containing channel with data as in the above function

        Returns
        -------

        """
        sq_command = "SELECT ip FROM channels WHERE name=?"
        for job in job_data:
            ip_addr = db_cur.execute(sq_command, job_data["channel_name"])
            out_path = os.path.join(__recording_dir__, job_data["channel_name"], job["name"])
            duration = job_data["duration"]
            job_time = job_data["start_time"]
            week_str = self._to_weekday(job_data["repetition"])
            job_name = job_data["name"]

            self._scheduler.add_recording_job(ip_addr=ip_addr, out_path=out_path, duration=duration,
                                              job_time=job_time, week_days=week_str,
                                              job_name=job_name)

    def display_jobs(self):
        """
        displays the list of scheduled jobs by calling appropriate
        Scheduler method

        Returns
        -------

        """
        LOG.info("Here is the list of all scheduled jobs:")
        self._scheduler.print_jobs()

    def rm_job(self):
        """
        removes a job from the schedule

        Returns
        -------

        """
        # job name, unique id of the job to be removed
        job_name = input("Job name: ")

        self._scheduler.rm_recording_job(job_name)

    @staticmethod
    def _to_weekday(entry):
        """
        converts the integer group to weekday string

        Parameters
        ----------
        entry
            type: int
            integer from, eg. 0001000 for only wednesday

        Returns
        -------
            type: str
            string containing short forms of weekdays

        """
        week_list = ["sun", "mon", "tue", "wed", "thurs", "fri", "sat"]
        week_str = []
        int_list = [int(x) for x in entry]
        for value, index in enumerate(int_list):
            if value:
                week_str.append(week_list[index])

        return " ".join(week_list)
