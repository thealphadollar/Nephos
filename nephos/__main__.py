"""
The file run when Nephos is called as a module
"""
import os
import sys
import logging
import time
import click

from . import __nephos_dir__
from .nephos import Nephos
from .ver_info import VER_INFO


# Here logger is defined manually since this is the first time the file launched 
# and has __name__ = "__main__"
LOG = logging.getLogger('nephos')


def multi_key_dict_get(multi_key_dict, key):
    """
    finds the value of a single key in a dictionary with tuple keys

    Parameters
    ----------
    multi_key_dict
        type: dict
        dictionary with tuple as keys
    key
        type: str
        key

    Returns
    -------
    Corresponding value of the key in dictionary if exists,
    None otherwise.

    """
    for keys, value in multi_key_dict.items():
        if key in keys:
            return value
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
    "add job", "adjb"\t\t\tadd a job using command line
    "list jobs", "lsjb"\t\t\tlist currently scheduled jobs
    "add channel, "adch"\t\tadd a channel using command line
    "list channels", "lsch"\t\tlist currently added channels
    "add share", "adsh"\t\t\tadd a new share entity with tags
    "list share", "lssh"\t\tlists present share entities in database
    "list tasks", "lstk"\t\tlists the recordings queue for processing and uploading
    "remove task", "rmtk"\t\tremove a task from queue using it's ID from 'lstk' 

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


@click.group(chain=True)
def main():
    """
    A minimalistic CLI to initiate Nephos; record, process, push!

    """
    pass


@main.command("init", help="initialise nephos home directory and config files")
def initialise():
    """
    initializes nephos home directory and config files

    Returns
    -------

    """
    Nephos.first_time()


@main.command("start", help="run nephos in the terminal")
def start():
    """
    runs nephos in the terminal

    """
    if not os.path.exists(__nephos_dir__):
        print("Error: first initialise Nephos directory using 'init' argument!")
        exit(1)

    client = Nephos()
    client.start()

    # provides functions to launch while scheduler in background
    cli = {
        ("help", "?"): runtime_help,
        ("add job", "adjb"): client.job_handler.add_job,
        ("list jobs", "lsjb"): client.job_handler.display_jobs,
        ("add channel", "adch"): client.channel_handler.add_channel,
        ("list channels", "lsch"): client.channel_handler.display_channel,
        ("add share", "adsh"): client.share_handler.add_share_entity,
        ("list share", "lssh"): client.share_handler.display_shr_entities,
        ("list tasks", "lstk"): client.preprocessor.display_tasks
        # ("remove task", "rmtk"): client.preprocessor.rm_task
        # ("adtk", "add task"): client.preprocessor.add_task
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
