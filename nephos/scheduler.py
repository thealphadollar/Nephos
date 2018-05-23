"""
All scheduler tasks go here.
"""

import os
from logging import getLogger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import time
from . import __nephos_dir__
from .recorder.channels import ChannelHandler

LOG = getLogger(__name__)

# config for the scheduler, not to be set by the user
PATH_JOB_DB = os.path.join(__nephos_dir__, "databases/jobs.db")
MAX_CONCURRENT_JOBS = 20
TMZ = time.tzname[time.daylight]


class Scheduler:
    """
    A class to rule all the scheduling related tasks.
    """
    def __init__(self):
        """
        initialise Scheduler with basic configuration
        """
        job_stores = {
            'default': SQLAlchemyJobStore(url='sqlite://' + PATH_JOB_DB)
        }
        executors = {
            'default': ThreadPoolExecutor(MAX_CONCURRENT_JOBS)
        }

        self._scheduler = BackgroundScheduler(jobstores=job_stores, executors=executors,
                                              timezone=TMZ)
        LOG.info("Scheduler initialised with database at %s", PATH_JOB_DB)

    def start(self):
        """
        Starts the scheduler
        Returns
        -------

        """
        self._scheduler.start()
        LOG.info("Scheduler started!")

    def add_recording_job(self, ip, out_path, duration, job_time, week_days, job_name):
        """
        Add recording jobs to the scheduler

        Parameters
        ----------
        ip
            type: str
            ip address of the channel
        out_path
            type: str
            path, without ".ts", where the file is to the saved
        duration
            type: int
            duration in minutes for the job to run
        job_time
            type: HH:MM
            time to begin the job
        week_days
            type: str
            contains the details for which week days the job is to run
        job_name
            type: str
            name of the job, unique

        Returns
        -------

        """
        hour, minute = job_time.split(":")
        duration_secs = 60 * duration
        job = self._scheduler.add_job(ChannelHandler.record(ip_addr=ip, addr=out_path,
                                                            duration_secs=duration_secs), trigger='cron',
                                      hour=hour, minute=minute, day_of_week=week_days, id=job_name,
                                      max_instances=1)
        LOG.info("Recording job added: %s", job)

    def add_maintenance_jobs(self, func, main_id, interval):
        """
        Add maintenance jobs to the scheduler

        Parameters
        ----------
        func
            type: callable
            maintenance function to be run at the execution of the job
        main_id
            type: str
            unique id to be associated with the job
        interval
            type: int
            repetition interval in minutes

        Returns
        -------

        """
        job = self._scheduler.add_job(func=func, trigger='interval',
                                      minutes=interval, id=main_id, max_instances=1, )
        LOG.info("Maintenance job added %s", job)

    def print_jobs(self):
        """
        prints a formatted list of jobs, their triggers and next run times

        Returns
        -------

        """
        self._scheduler.print_jobs()

    def rm_recording_job(self, job_id):
        """
        delete a recording job from schedule

        Parameters
        ----------
        job_id
            type: str
            unique id (most probably name) of the job
        Returns
        -------

        """
        self._scheduler.remove_job(job_id)
        LOG.info("%s job removed from schedule", job_id)
