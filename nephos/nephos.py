"""
The pipeline for the working of nephos
"""
from abc import ABC
from logging import getLogger
import sys
from . import first_time
from .exceptions import DBException
from .load_config import Config
from .manage_db import DBHandler
from .scheduler import Scheduler
from .recorder.channels import ChannelHandler
from .recorder.jobs import JobHandler
from .maintenance.main import Maintenance
from .maintenance.single_instance import SingleInstance
from .exceptions import SingleInstanceException


LOG = getLogger(__name__)


# Creates a PID file and locks on to it so only one running instance of Nephos possible at a time.
# https://stackoverflow.com/a/1265445
try:
    _ = SingleInstance()
except SingleInstanceException as err:
    LOG.error(err)
    sys.exit(-1)


class Nephos(ABC):
    """
    The abstract base class from which new derived classes can be created to support varying
    online storage platforms.

    """

    def __init__(self):
        """
        initiates Nephos with basic configuration, modules and makes it ready to be started.
        """
        first_time_init = None
        if first_time():
            print("This is the first time Nephos is being run; copied necessary files.")
            first_time_init = True

        # loading and setting configuration
        self.config_handler = Config()
        self.config_handler.load_config()
        self.config_handler.initialise()
        LOG.info("Configuration completed!")

        LOG.info("Loading database, scheduler, maintenance modules...")
        self.db_handler = DBHandler()
        self.scheduler = Scheduler()
        self.channel_handler = ChannelHandler()
        self.job_handler = JobHandler(self.scheduler)
        self.maintenance_handler = Maintenance(self.config_handler.maintenance_config)

        if first_time_init:
            self.db_handler.first_time()
            self.db_handler.init_jobs_db()
            self.maintenance_handler.add_maintenance_to_scheduler(self.scheduler)

        LOG.info("Nephos is all set to launch")

    def start(self):
        """
        Start nephos, with the background processes.

        Returns
        -------

        """

        self.scheduler.start()

    def load_channels_sharelist(self):
        """
        loads data from a file which contains both channels and share entities
        Segregates them based on the dictionary key and then passes the dictionary to
        appropriate functions in recorder and uploader.

        Returns
        -------

        """
        data_file = input("File path: ")

        data = self.config_handler.load_data(data_file, False)
        try:
            with self.db_handler.connect() as db_cur:
                try:
                    self.channel_handler.insert_channels(db_cur, data["channels"])
                except KeyError as error:
                    LOG.warning("No channel data found!")
                    LOG.debug(error)
                # TODO: Function to manage share_lists
        except DBException as error:
            LOG.warning("Data addition failed")
            LOG.debug(error)
