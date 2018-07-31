"""
Ensures only one Nephos running at a time.
Source: https://github.com/pycontribs/tendo/blob/master/tendo/singleton.py
"""
from logging import getLogger
import os
import sys
import tempfile
import fcntl
from ..exceptions import SingleInstanceException

LOG = getLogger(__name__)


class SingleInstance:
    """
    Class that can be instantiated only once per machine.
    If is there another instance already running it will throw a `SingleInstanceException`.
    This works by creating a lock file with a filename based on the full path to the script file.

    """

    def __init__(self, flavor_id=""):
        """
        Instantiate the class with the checking and creation of PID file.

        """
        self.initialized = False
        basename = os.path.splitext(os.path.abspath(sys.argv[0]))[0].replace(
            "/", "-").replace(":", "").replace("\\", "-") + '-%s' % flavor_id + '.lock'

        self.lockfile = os.path.normpath(
            tempfile.gettempdir() + '/' + basename)

        LOG.debug("SingleInstance lockfile: %s", self.lockfile)
        self.file_path = open(self.lockfile, 'w')
        self.file_path.flush()
        try:
            fcntl.lockf(self.file_path, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            print("Nephos is already running, quitting!")
            raise SingleInstanceException()
        self.initialized = True

    def __del__(self):

        if not self.initialized:
            return
        try:
            fcntl.lockf(self.file_path, fcntl.LOCK_UN)
            if os.path.isfile(self.lockfile):
                os.unlink(self.lockfile)
        except OSError as error:
            LOG.warning("Error in unlocking PID file!")
            LOG.debug(error)
            sys.exit(-1)
