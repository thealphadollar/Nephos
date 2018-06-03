"""
The file run when Nephos is called as a module
"""
import sys
import logging
import time
import click
from .nephos import Nephos
from .ver_info import VER_INFO


# Here logger defined manually since this is the first file launched and has __name__ = "__main__"
LOG = logging.getLogger('nephos')


def runtime_help():
    """
    Provides help for options during runtime

    Returns
    -------

    """
    print('''
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


def stop(scheduler):
    """
    stops nephos' scheduler after finishing running jobs

    Parameters
    ----------
    scheduler
        type: APS background scheduler
        current running instance of Nephos class

    Returns
    -------

    """
    scheduler.shutdown()
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
        "load batch jobs": client.job_handler.load_jobs,
        "add job": client.job_handler.add_job,
        "list jobs": client.job_handler.display_jobs,
        "remove job": client.job_handler.rm_job,
        "add data": client.load_channels_sharelist,
        "add channel": client.channel_handler.add_channel,
        "list channels": client.channel_handler.display_channel,
        "remove channel": client.channel_handler.delete_channel
    }

    LOG.info("NOTE: enter commands during runtime to perform operations over nephos, try \"help\"!")

    while True:
        command = input("\nEnter command to perform:\n").lower()
        if command in cli.keys():
            cli[command]()
        elif command in ["ver", "version", "info"]:
            print(VER_INFO)
        elif command in ["quit", "exit", "stop"]:
            stop(client.scheduler)
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
    print(VER_INFO)


if __name__ == '__main__':
    main()
