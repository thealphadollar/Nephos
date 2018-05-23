"""
The file run when Nephos is called as a module
"""
import logging
from .nephos import Nephos


# Here logger defined manually since this is the first file launched and has __name__ = "__main__"
LOG = logging.getLogger('nephos')


def main():  # TODO: More work on this, temporary
    """
    Called when nephos run as a package
    Returns
    -------

    """
    client = Nephos()
    client.start()


if __name__ == '__main__':
    main()
