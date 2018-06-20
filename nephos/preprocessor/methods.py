"""
Contains all the methods applied in preprocessing
"""
import subprocess
import json
from logging import getLogger
from . import get_preprocessor_config
from ..manage_db import DBHandler, DBException

LOG = getLogger(__name__)
SET_PROCESSING_COMMAND = """UPDATE tasks
                    SET status = "processing"
                    WHERE orig_path = ?"""


class ApplyProcessMethods:

    def __init__(self, path_to_file, store_path):
        """
        Loads the file to be processed and applies all the methods till new file output.

        Parameters
        ----------
        path_to_file
            type: str
            path to file to be processed
        store_path
            type: str
            path to directory to store the files, post-processing

        """
        self.addr = path_to_file
        self.store = store_path
        self.config = get_preprocessor_config()
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(SET_PROCESSING_COMMAND, (path_to_file,))
        except DBException as error:
            LOG.warning("Couldn't connect to database for %s", path_to_file)
            LOG.debug(error)

        # TODO: Create a custom exception which on call will erase all work done and revert the
        # TODO: status to "not processed"


def get_lang(path_to_file):
    """
    Uses ffprobe to gather information about languages present in the stream.

    Parameters
    ----------
    path_to_file
        type: str
        path to file to be processed

    Returns
    -------
    aud_lang
        type: str
        audio languages
    sub_lang
        type: str
        subtitle languages

    """
    aud_lang = []
    sub_lang = []
    path_ffprobe = get_preprocessor_config()['path_to_ffprobe']
    cmd = "{path_ffprobe} -v quiet -print_format json -show_streams {path_to_file}".format(
        path_ffprobe=path_ffprobe,
        path_to_file=path_to_file
    )
    try:
        lang_data = json.loads(subprocess.check_output(cmd, shell=True))
        for data in lang_data["streams"]:
            if data["codec_type"] == "audio":
                lang = data["tags"]["language"].lower()
                if lang not in aud_lang:
                    aud_lang.append(lang)
            elif data["codec_type"] == "subtitle":
                lang = data["tags"]["language"].lower()
                if lang not in sub_lang:
                    sub_lang.append(lang)
    except subprocess.CalledProcessError as error:
        LOG.warning("ffprobe failed for %s", path_to_file)
        LOG.debug(error)

    return " ".join(aud_lang), " ".join(sub_lang)
