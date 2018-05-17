"""
Contains class for the checking of channel, whether online or not
"""
from logging import getLogger

LOG = getLogger(__name__)


class ChannelOnlineCheck:
    """
    Checks whether all the channels are online or not and
    prepares a report of the number of channels up, down and
    the magnitude of change.
    """

    def __init__(self, config_maintain):
        pass
