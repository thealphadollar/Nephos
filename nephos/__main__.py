"""
The file run when Nephos is called as a module
"""
import sys
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
    
    "help"\t\tshow help
    "version"\t\tshow version
    "stop"\t\tstop nephos after completion of running jobs
    "load batch jobs"\t\tload jobs from add_jobs file
    "add job"\t\tadd a job using command line
    "list jobs"\t\tlist currently scheduled jobs
    "remove job"\t\tremove job using job name
    "add data"\t\tadd channels and share entities
    "add channel\t\tadd a channel using command line
    "list channels"\t\tlist currently added channels
    "remove channel"\t\tremove channel using ip or name

    For more details, see the docs present in $HOME/Nephos
    ==========
    ''')


def stop(client):
    """
    stops nephos' scheduler after finishing running jobs

    Parameters
    ----------
    client
        type: Nephos class
        current running instance of Nephos class

    Returns
    -------

    """
    client.Scheduler.shutdown()
    return


@click.group(chain=True)
def main():
    """
    A minimalistic CLI to initiate Nephos; record, process, push!

    """
    pass


@main.command("start", help="run nephos in the terminal")
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

    LOG.info("NOTE: enter commands during runtime to perform operations over nephos, try \"help\"!")

    while True:
        command = input("\nEnter command to perform:\n").lower()
        if command in cli.keys():
            cli[command]()
        elif command in ["ver", "version", "info"]:
            click.echo(ver_info)
        elif command in ["quit", "exit", "stop"]:
            stop(client)
            LOG.warning("Nephos Stopped!")
            sys.exit(0)
        else:
            LOG.error("Unrecognised operation \'%s\', use \'help\' to know more.", command)

        time.sleep(1)


@main.command("version", help="shows version and other information")
def print_ver_info():
    """
    displays information related to development cycle

    """
    click.echo(ver_info)


if __name__ == '__main__':
    main()
