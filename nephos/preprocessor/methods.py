"""
Contains all the methods applied in preprocessing
"""
import subprocess
import json
from logging import getLogger
from . import get_preprocessor_config

LOG = getLogger(__name__)


class ApplyProcessMethods:

    def __init__(self, path_to_file):
        """
        Loads the file to be processed and applies all the methods till new file output.

        Parameters
        ----------
        path_to_file
            type: str
            path to file to be processed

        """
        self.addr = path_to_file
        # TODO: Complete this


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
