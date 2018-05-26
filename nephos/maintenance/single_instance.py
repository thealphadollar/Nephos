"""
Ensures only one Nephos running at a time.
Source: https://github.com/pycontribs/tendo/blob/master/tendo/singleton.py
"""
from logging import getLogger
import os
import sys
import tempfile
import fcntl
from ..custom_exceptions import SingleInstanceException

LOG = getLogger(__name__)


class SingleInstance(object):
    """
    Class that can be instantiated only once per machine.
    If you want to prevent your script from running in parallel just instantiate SingleInstance() class.
    If is there another instance already running it will throw a `SingleInstanceException`.
    This option is very useful if you have scripts executed by crontab at small amounts of time.
    Remember that this works by creating a lock file with a filename based on the full path to the script file.

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

        LOG.debug("SingleInstance lockfile: " + self.lockfile)
        self.fp = open(self.lockfile, 'w')
        self.fp.flush()
        try:
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            LOG.warning("Nephos is already running, quitting!")
            raise SingleInstanceException()
        self.initialized = True

    def __del__(self):

        if not self.initialized:
            return
        try:
            if sys.platform == 'win32':
                if hasattr(self, 'fd'):
                    os.close(self.fd)
                    os.unlink(self.lockfile)
            else:
                fcntl.lockf(self.fp, fcntl.LOCK_UN)
                # os.close(self.fp)
                if os.path.isfile(self.lockfile):
                    os.unlink(self.lockfile)
        except Exception as e:
            LOG.error(e)
            sys.exit(-1)
