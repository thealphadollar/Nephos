"""
Contains classes used for logging through logger.YAML config file
"""

import os
import logging


class EnsureFolderFileHandler(logging.FileHandler):
    """
    Ensures that the directory specified for the log file exists
    """
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        """

        Parameters
        ----------
        filename
            type: str
            Compulsory parameter, path to the file to be used to store logs
        mode
            type: str
            default: 'a'
            Specifies the method in which log file is to be opened
        encoding
            type: str
            default: None
            Specifies the encoding in which file is to be opened
        delay
            type: bool
            default: False
            If delay is true, then file opening is deferred until the first call to emit()
            https://docs.python.org/3/library/logging.handlers.html#logging.FileHandler.emit

        """

        # make directory if not present
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        logging.FileHandler.__init__(self, filename, mode, encoding, delay)
