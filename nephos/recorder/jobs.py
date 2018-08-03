"""
Stores all code related to recording jobs
"""

import os
from logging import getLogger
from sqlite3 import InterfaceError

from .. import __recording_dir__, validate_entries
from ..manage_db import DBHandler
from ..exceptions import DBException


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
        start_time = str(input("Start time [HH:MM]: "))
        duration = int(input("Duration [in minutes]: "))
        rep = str(input("Run on [eg. 1010000 for monday and wednesday]: "))
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
                self.insert_jobs(db_cur, validate_entries(job_data))
        except DBException as err:
            LOG.warning("Data addition failed")
            LOG.debug(err)

    def load_jobs(self, data):
        """
        loads data from a file which contains jobs
        Segregates them based on the dictionary key and then passes the dictionary to
        appropriate functions in JobHandler.

        Parameters
        ----------
        data
            type: dict
            contains the list of new jobs to be added to database

        Returns
        -------
        type: bool
        True if operations were successful, False otherwise

        """
        try:
            with DBHandler.connect() as db_cur:
                self.insert_jobs(db_cur, data)
            return True
        except DBException as err:
            LOG.warning("Data addition failed")
            LOG.debug(err)
            return False

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
            dict containing channel with data as in the add_job function

        Returns
        -------

        """
        sql_command = "SELECT ip FROM channels WHERE name=?"
        for job_key in job_data.keys():
            try:
                job_data[job_key]["channel_name"] = "_".join(
                    job_data[job_key]["channel_name"].lower().split()
                )
                db_cur.execute(sql_command, (job_data[job_key]["channel_name"], ))
                try:
                    ip_addr = db_cur.fetchall()[0][0]
                except IndexError as err:
                    LOG.info("No channel %s found!", job_data[job_key]["channel_name"])
                    LOG.debug(err)
                    return
                out_path = os.path.join(__recording_dir__, job_data[job_key]["channel_name"],
                                        job_data[job_key]["name"])
                duration = job_data[job_key]["duration"]
                job_time = str(job_data[job_key]["start_time"])
                week_str = self.to_weekday(job_data[job_key]["repetition"])
                job_name = "_".join(job_data[job_key]["name"].lower().split())

                self._scheduler.add_recording_job(ip_addr=ip_addr, out_path=out_path,
                                                  duration=duration,
                                                  job_time=job_time, week_days=week_str,
                                                  job_name=job_name)
            except InterfaceError as error:
                LOG.warning('No channel %s in database!', job_data[job_key]["channel_name"])
                LOG.debug(error)

    def display_jobs(self):
        """
        displays the list of scheduled jobs by calling appropriate
        Scheduler method

        Returns
        -------

        """
        job_list = self._scheduler.get_jobs()
        for job in job_list:
            print("Name: " + job.id, "\tNextRun: ", job.next_run_time)

    def rm_jobs(self, job_data):
        """
        removes a job from the schedule

        Parameters
        ----------
        job_data
            type: dict
            dict containing the list of jobs to be added

        Returns
        -------

        """
        # job name, unique id of the job to be removed
        for job_key in job_data.keys():
            job_name = "_".join(job_data[job_key]["name"].lower().split())
            self._scheduler.rm_recording_job(job_name)

    @staticmethod
    def to_weekday(entry):
        """
        converts the integer group to weekday string

        Parameters
        ----------
        entry
            type: str
            integer from, eg. 0001000 for only wednesday

        Returns
        -------
            type: str
            string containing short forms of weekdays

        """
        week_list = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        week_str = []
        int_list = [int(x) for x in entry]
        for index, value in enumerate(int_list):
            if value:
                week_str.append(week_list[index])

        return ",".join(week_str)
