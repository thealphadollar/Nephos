"""
The file run when Nephos is called as a module
"""
import logging
import click
import time
from .nephos import Nephos
from .ver_info import ver_info


# Here logger defined manually since this is the first file launched and has __name__ = "__main__"
LOG = logging.getLogger('nephos')


def runtime_help():
    """
    Provides help for options during runtime

    Returns
    -------

    """
    click.echo('''
    ==========
    You can enter the following options while nephos is
    running to perform various operations.
    
    "help"\tShows help
    "load batch jobs"\tload jobs from add_jobs file
    "add job"\tadd a job using command line
    "list jobs"\tlist currently scheduled jobs
    "remove job"\tremove job using job name
    "add data"\tadd channels and share entities
    "add channel\tadd a channel using command line
    "list channels"\tlist currently added channels
    "remove channel"\tremove channel using ip or name''')

@click.group(chain=True)
def main():
    """
    A minimalistic CLI to operation Nephos; record, process, push!

    """
    pass


@main.command("-s", "--start", help="run nephos in the terminal")
def start():
    """
    run nephos in the terminal

    """
    client = Nephos()
    client.start()

    # provides functions to launch while scheduler in background
    cli = {
        "help": runtime_help,
        "load batch jobs": client.JobHandler.load_jobs,
        "add job": client.JobHandler.add_job,
        "list jobs": client.JobHandler.display_jobs,
        "remove job": client.JobHandler.rm_job,
        "add data": client.load_channels_sharelist,
        "add channel": client.ChannelHandler.add_channel,
        "list channels": client.ChannelHandler.display_channel,
        "remove channel": client.ChannelHandler.delete_channel
    }

    LOG.info("NOTE: enter commands anytime to perform operations over nephos, try \"help\"!")

    while True:
        command = input("Enter command to perform: ")
        if command in cli.keys():
            cli[command]()
        else:
            LOG.error("Unrecognised operation %s, use \"help\" to know more.", command)

        time.sleep(10)


@click.command("-v", "--version", help="shows version and other information")
def print_ver_info():
    """
    displays information related to development cycle

    """
    print(ver_info)


if __name__ == '__main__':
    main()
