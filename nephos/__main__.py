"""
The file run when Nephos is called as a module
"""

from . import first_time
from .load_config import load_config


def main():  # TODO: More work on this, temporary
    """
    Called when nephos run as a package
    Returns
    -------

    """
    first_time()
    load_config()


if __name__ == '__main__':
    main()

