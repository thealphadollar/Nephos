"""
All scheduler tasks go here.
"""

import os
from logging import getLogger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from pytz import utc
from . import __nephos_dir__

LOG = getLogger(__name__)

# config for the scheduler, not to be set by the user
PATH_JOB_DB = os.path.join(__nephos_dir__, "databases/jobs.db")
MAX_CONCURRENT_JOBS = 20


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

        self._scheduler = BackgroundScheduler(jobstores=job_stores, executors=executors)
        LOG.info("Scheduler initialised with database at %s", PATH_JOB_DB)

    def start(self):
        """
        Starts the scheduler
        Returns
        -------

        """
        self._scheduler.start()
        LOG.info("Scheduler started!")

    
