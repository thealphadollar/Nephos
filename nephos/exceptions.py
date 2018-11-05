"""
Contains custom errors and exceptions for Nephos
"""
import shutil
import os
from logging import getLogger

from .mail_notifier import add_to_report


LOG = getLogger(__name__)
UNSET_PROCESSING_COMMAND = """UPDATE tasks
                            SET status = "not processed"
                            WHERE orig_path = ?"""
UNSET_UPLOADING_COMMAND = """UPDATE tasks
                            SET status = "processed"
                            WHERE store_path = ?"""
REMOVE_ENTRY = """DELETE
            FROM tasks
            WHERE orig_path = ?"""
INCREMENT_FAIL_COUNT = """UPDATE tasks
            SET fail_count = fail_count + 1
            WHERE orig_path = ?"""
GET_FAIL_COUNT = """SELECT fail_count
            FROM tasks
            WHERE orig_path = ?"""


class DBException(Exception):
    """
    Handles exceptions concerning Database
    """
    pass


class SingleInstanceException(BaseException):
    """
    Handles exception raised by SingleInstance class
    """
    pass


class ProcessFailedException(Exception):
    """
    Handles exceptions concerned with failures of preprocessing
    """
    def __init__(self, path_to_file, store_path, db_cur, error):
        """

        Parameters
        ----------
        path_to_file
            type: str
            path to the original file
        store_path
            type: str
            path to the folder for storing processed files
        db_cur
            sqlite database cursor
        error
            type: str
            error causing processing to fail
        """
        self.path_file = path_to_file
        self.to_clr_dir = store_path
        self.db_cur = db_cur
        self.error = error
        self._clear()
        super(ProcessFailedException, self).__init__()

    def _clear(self):
        """
        Clears the directory of any left over files if preprocessing fails at any step
        And modifies "status" of file to "not processed" in database

        Returns
        -------

        """

        # getting fail count
        self.db_cur.execute(GET_FAIL_COUNT, (self.path_file, ))
        fail_count = self.db_cur.fetchall()[0][0]

        if fail_count == 2:
            self.db_cur.execute(REMOVE_ENTRY, (self.path_file, ))
            shutil.rmtree(self.to_clr_dir)
            os.remove(self.path_file)
            msg = "Following file has been removed due to multiple failures in " \
                  "processing:\n{file_path}".format(file_path=self.path_file)
            LOG.critical(msg)
            add_to_report("{file} discarded from Nephos queue due to multiple processing"
                          " failures with following error:\n{error}\n".format(
                              file=self.path_file,
                              error=self.error
                          ))

        else:
            self.db_cur.execute(UNSET_PROCESSING_COMMAND, (self.path_file, ))
            self.db_cur.execute(INCREMENT_FAIL_COUNT, (self.path_file, ))
            shutil.rmtree(self.to_clr_dir)
            LOG.warning("Following file reverted due to error in preprocessing, "
                        "%d tries remaining before removal: \n%s", 2-fail_count, self.path_file)


class UploadingFailed(Exception):
    """
    Handles failure of uploading and reverts the status back to processed.
    """
    def __init__(self, store_path, db_cur):
        # TODO: this is not working
        db_cur.execute(UNSET_UPLOADING_COMMAND, (store_path, ))
        super(UploadingFailed, self).__init__()


class OAuthFailure(Exception):
    """
    Handles all authentication failure
    """
    pass


class FTPFailure(Exception):
    """
    Handles all FTP failures and exceptions raised
    """
    def __init__(self):
        LOG.error("FTP upload failed!")
        super(FTPFailure, self).__init__()


class UpdateDataFailure(Exception):
    """
    Handles all Update Data failures and exceptions raised
    """
    pass
