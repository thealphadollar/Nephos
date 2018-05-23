"""
The file run when Nephos is called as a module
"""
import logging
import click
from .nephos import Nephos


# Here logger defined manually since this is the first file launched and has __name__ = "__main__"
LOG = logging.getLogger('nephos')


@click.command()
@click.argument("--operation", prompt="Operation to perform",
                help="Perform various Nephos operations")
def main():  # TODO: More work on this, temporary
    """
    Called when nephos run as a package
    Returns
    -------

    """
    pass


if __name__ == '__main__':
    client = Nephos()
    client.start()
    main()
