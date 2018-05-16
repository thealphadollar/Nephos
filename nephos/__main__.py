"""
The file run when Nephos is called as a module
"""

from . import first_time
import logging
from .load_config import Config

# Here logger defined manually since this is the first file launched and has __name__ = "__main__"
log = logging.getLogger('nephos')


def main():  # TODO: More work on this, temporary
    """
    Called when nephos run as a package
    Returns
    -------

    """
    first_time()
    config = Config()
    config.load_config()
    config.initialise()
    log.info("Test passed")
    log.critical("mail check")


if __name__ == '__main__':
    main()
