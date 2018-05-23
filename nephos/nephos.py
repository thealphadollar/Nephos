"""
The pipeline for the working of nephos
"""
from abc import ABC
import click
from logging import getLogger
from . import first_time
from .custom_exceptions import DBException
from .load_config import Config
from .manage_db import DBHandler
from .scheduler import Scheduler
from .recorder.channels import ChannelHandler
from .recorder.jobs import JobHandler
from .maintenance import Maintenance

LOG = getLogger(__name__)


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
            click.echo("This is the first time Nephos is being run; copied necessary files.")
            first_time_init = True

        # loading and setting configuration
        self.ConfigHandler = Config()
        self.ConfigHandler.load_config()
        self.ConfigHandler.initialise()
        LOG.info("Configuration loaded!")

        LOG.info("Loading database, scheduler, maintenance modules...")
        self.DBHandler = DBHandler()

        self.Scheduler = Scheduler()
        self.ChannelHandler = ChannelHandler()
        self.JobHandler = JobHandler(Scheduler)
        self.MaintenanceHandler = Maintenance(self.ConfigHandler.maintenance_config)

        if first_time_init:
            self.DBHandler.first_time()
            self.ConfigHandler.add_maintenance_to_scheduler(self.Scheduler, self.MaintenanceHandler)

        LOG.info("Nephos is all set to launch")

    def start(self):
        """
        Start nephos, with the background processes

        Returns
        -------

        """
        self.Scheduler.start()
        LOG.info("Nephos is running")

    @click.command()
    @click.option("--file", prompt="File path", help="path to the data file")
    def load_jobs(self, data_file):
        """
        loads data from a file which contains jobs
        Segregates them based on the dictionary key and then passes the dictionary to
        appropriate functions in JobHandler.

        Parameters
        -------
        data_file
            type: str
            path to the data file

        Returns
        -------

        """
        data = self.ConfigHandler.load_data(data_file)
        try:
            with self.DBHandler.connect() as db_cur:
                self.JobHandler.insert_jobs(db_cur, data)
        except DBException as err:
            LOG.warning("Data addition failed")
            LOG.error(err)

    @click.command()
    @click.option("--file", prompt="File path", help="path to the data file")
    def load_data(self, data_file):
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
        data = self.ConfigHandler.load_data(data_file)
        try:
            with self.DBHandler.connect() as db_cur:
                self.ChannelHandler.insert_channels(db_cur, data["channels"])
                # TODO: Function to manage share_lists
        except DBException as err:
            LOG.warning("Data addition failed")
            LOG.error(err)
