"""
An abstract Checker class for all checks, adding new checks made easier through this API
"""
from abc import ABC, abstractmethod
from logging import getLogger
import pydash

from ..mail_notifier import send_mail

LOG = getLogger(__name__)


class Checker(ABC):
    """
    Derive all maintenance jobs from this and direct their result to
    _handler function.

    Compulsory method for the derived classes:
        _execute()
    """

    def __init__(self, config_maintain):
        """
        Configures checker for low disk space.

        Parameters
        ----------
        config_maintain
            type: dictionary
            contains information for maintenance task
        """
        self.config = config_maintain

    def to_run(self, kind):
        """
        Checks from config file if the maintenance job is to be executed

        Parameters
        -------
        kind
            type: str
            kind of the job to be executed

        Returns
        -------
        executes self._executed() if to be executed
        displays warning log otherwise

        """

        if self._get_data(kind, "enabled"):
            self._execute()

        else:
            LOG.warning("%s maintenance job is not enabled", kind)

    @abstractmethod
    def _execute(self):
        """
        TO BE OVERRIDDEN IN DERIVED CLASS
        method to execute the checks should go here
        Returns
        -------

        """
        pass

    @staticmethod
    def _handle(is_critical, msg_type, msg):
        """
        Handles the evaluation results of the maintenance jobs
        Uses,
            LOG.critical for logging error
            send_mail  for sending critical mail
            LOG.info for displaying information regarding exceptions
            LOG.debug for writing detailed error report to nephos.txt logs

        Parameters
        ----------
        is_critical
            type: bool
            True if the issue is critical, False otherwise
        msg_type
            type: str
            states the type of message to be handled
        msg
            type: str
            message to be logged

        Returns
        -------

        """
        if is_critical:
            # below line sends an email and catches exception if any
            LOG.critical(msg)
            if msg_type != "ch_down":
                send_mail(msg, msg_type)

        else:
            LOG.info(msg)

    def _get_data(self, kind, keyword):
        """
        Grabs data from the config dict

        Parameters
        ----------
        keyword
            type: str
            data to be grabbed

        Returns
        -------
            type: depends on the key's value
            value of the data for the key queried

        """
        data_point = "jobs.{kind}.{keyword}".format(kind=kind, keyword=keyword)
        return pydash.get(self.config, data_point)
