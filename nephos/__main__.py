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


def multi_key_dict_get(d, k):
    for keys, v in d.items():
        if k in keys:
            return v
    return None


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
    
    "help", "?"\t\t\t\tshow help
    "version", "ver"\t\t\tshow version
    "stop", "st"\t\t\tstop nephos after completion of running jobs
    "load batch jobs", "ldjb"\t\tload jobs from add_jobs file
    "add job", "adjb"\t\t\tadd a job using command line
    "list jobs", "lsjb"\t\t\tlist currently scheduled jobs
    "remove job", "rmjb"\t\tremove job using job name
    "add data", "adda"\t\t\tadd channels and share entities
    "add channel, "adch"\t\tadd a channel using command line
    "list channels", "lsch"\t\tlist currently added channels
    "remove channel", "rmch"\t\tremove channel using ip or name

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
        ("help", "?"): runtime_help,
        ("load batch jobs", "ldjb"): client.job_handler.load_jobs,
        ("add job", "adjb"): client.job_handler.add_job,
        ("list jobs", "lsjb"): client.job_handler.display_jobs,
        ("remove job", "rmjb"): client.job_handler.rm_job,
        ("add data", "adda"): client.load_channels_sharelist,
        ("add channel", "adch"): client.channel_handler.add_channel,
        ("list channels", "lsch"): client.channel_handler.display_channel,
        ("remove channel", "rmch"): client.channel_handler.delete_channel
    }

    LOG.info("NOTE: enter commands during runtime to perform operations over nephos, try \"help\"!")

    while True:
        command = input("\nEnter command to perform:\n").lower()
        if multi_key_dict_get(cli, command) is not None:
            multi_key_dict_get(cli, command)()
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
