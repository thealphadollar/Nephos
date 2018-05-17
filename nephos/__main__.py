"""
The file run when Nephos is called as a module
"""
import logging
from . import first_time
from .load_config import Config
from .maintenance import Maintenance

# Here logger defined manually since this is the first file launched and has __name__ = "__main__"
LOG = logging.getLogger('nephos')


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
    LOG.info("Test passed")
    LOG.critical("mail check")
    maintenance = Maintenance(config.maintenance_config)
    maintenance.run_disk_space_check()


if __name__ == '__main__':
    main()
