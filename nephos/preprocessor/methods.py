"""
Contains all the methods applied in preprocessing
"""
import os
import subprocess
import json
from logging import getLogger

from . import get_preprocessor_config
from .share_handler import ShareHandler
from .. import __config_dir__
from ..manage_db import DBHandler, SL_MAIL_INDEX, SL_TAG_INDEX, \
    TSK_CHNAME_INDEX, TSK_LANG_INDEX, TSK_SUBLANG_INDEX, CH_COUN_INDEX, \
    CH_LANG_INDEX, CH_TMZ_INDEX
from ..exceptions import DBException, ProcessFailedException


LOG = getLogger(__name__)
SET_PROCESSING_COMMAND = """UPDATE tasks
                    SET status = "processing"
                    WHERE orig_path = ?"""
SET_PROCESSED_COMMAND = """UPDATE tasks
                    SET status = "processed"
                    WHERE orig_path = ?"""
SET_SHARE_COMMAND = """UPDATE tasks
                    SET share_with = ?
                    WHERE orig_path = ?"""
GET_TASK_INFO = """SELECT *
                FROM tasks
                WHERE orig_path = ?"""
GET_CH_INFO = """SELECT *
                FROM channels
                WHERE name = ?"""
PATH_TO_PROCESSING_SCRIPT = os.path.join(__config_dir__, "processing.sh")
MIN_BYTES = 1024  # 1KB


class ApplyProcessMethods:
    """
    Handles application of pipeline of processing the recording and
    eventually updating the database.
    """

    def __init__(self, path_to_file, store_path):
        """
        Loads the file to be processed, modifies status to "processing" and calls
        apply_methods on it.

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
        self.name = self._get_name()
        self.store_dir = store_path
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(SET_PROCESSING_COMMAND, (self.addr, ))
            self._apply_methods()
        except DBException as error:
            LOG.warning("Couldn't connect to database for %s", path_to_file)
            LOG.debug(error)

    def _apply_methods(self):
        """
        Applies the required methods over the provided file.

        Returns
        -------

        """
        try:
            os.makedirs(self.store_dir, exist_ok=True)
            self._execute_processing()
            self._add_share_entities()
            try:
                os.remove(self.addr)
            except FileNotFoundError as err:
                LOG.debug(err)
            try:
                with DBHandler.connect() as db_cur:
                    db_cur.execute(SET_PROCESSED_COMMAND, (self.addr, ))
            except DBException as err:
                LOG.debug(err)

        except ProcessFailedException as _:
            pass

    def _execute_processing(self):
        """
        Executes the script for processing of the recording

        Raises
        -------
        ProcessFailedException
            In case of exit code not 0 from command or output file not appropriate
        """
        failed = False
        out_file_mp4 = os.path.join(self.store_dir, self.name + ".mp4")
        cmd = '{path_script} "{INPUT}" "{OUT_FILE_WITHOUT_EXTENSION}" "{OUT_FOLDER}"'.format(
            path_script=PATH_TO_PROCESSING_SCRIPT,
            INPUT=self.addr,
            OUT_FILE_WITHOUT_EXTENSION=self.name,
            OUT_FOLDER=self.store_dir
        )
        try:
            LOG.debug("running command: %s", cmd)
            conversion_process = subprocess.Popen(cmd,
                                                  shell=True,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.STDOUT)
            output, _ = conversion_process.communicate()
            LOG.debug(output)
        except subprocess.CalledProcessError as err:
            LOG.debug(err)
            error = err
            failed = True

        try:
            if os.stat(out_file_mp4).st_size < MIN_BYTES:
                failed = True
        except FileNotFoundError as err:
            LOG.debug(err)
            error = err
            failed = True

        if failed:
            try:
                with DBHandler.connect() as db_cur:
                    raise ProcessFailedException(self.addr, self.store_dir, db_cur, error)
            except DBException as err:
                LOG.debug(err)

    # def _extract_subtitles(self):
    #     """
    #     Extracts subtitles using provided CCExtractor
    #     Returns
    #     -------
    #
    #     """
    #     path_ccextractor = self.config["path_to_CCEx"]
    #     ccex_args = self.config["CCEx_args"]
    #     out_file = os.path.join(self.store_dir, self.name + ".srt")
    #
    #     cmd = "{path_ccextractor} {input} {args} -o {output}".format(
    #         path_ccextractor=path_ccextractor,
    #         input=self.addr,
    #         args=ccex_args,
    #         output=out_file
    #     )
    #     self._execute(cmd, out_file)
    #
    # def _convert_to_mp4(self):
    #     """
    #     Converts the video to mp4 format using ffmpeg
    #     Returns
    #     -------
    #
    #     """
    #     path_ffmpeg = self.config["path_to_ffmpeg"]
    #     ffmpeg_args = self.config["ffmpeg_args"]
    #     out_file = os.path.join(self.store_dir, self.name + ".mp4")
    #
    #     cmd = "{path_ffmpeg} -i {input} {args} {output}".format(
    #         path_ffmpeg=path_ffmpeg,
    #         input=self.addr,
    #         args=ffmpeg_args,
    #         output=out_file
    #     )
    #     self._execute(cmd, out_file)

    def _add_share_entities(self):
        """
        Appends share entities to the file querying share_list database.

        Returns
        -------

        """
        valid_entities = []
        all_entities = ShareHandler.grab_shr_list()
        tags_for_file = self._assemble_tags()

        for entity in all_entities:
            if self._tag_match(entity[SL_TAG_INDEX].split(), tags_for_file.split()):
                valid_entities.append(entity[SL_MAIL_INDEX])
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(SET_SHARE_COMMAND, (" ".join(valid_entities), self.addr, ))
        except DBException as err:
            LOG.debug(err)

    def _assemble_tags(self):
        """
        Assembles all tags for the current file

        Returns
        -------
        str containing multiple tags separated by space

        """
        tags = []

        # getting data from tasks tables
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(GET_TASK_INFO, (self.addr, ))
                task_info = db_cur.fetchall()[0]
            tags.append(task_info[TSK_CHNAME_INDEX])
            tags.append(task_info[TSK_LANG_INDEX])
            tags.append(task_info[TSK_SUBLANG_INDEX])
        except DBException as err:
            LOG.debug(err)

        # getting data from channels table
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(GET_CH_INFO, (task_info[TSK_CHNAME_INDEX], ))
                ch_info = db_cur.fetchall()[0]
            tags.append(ch_info[CH_COUN_INDEX])
            tags.append(ch_info[CH_TMZ_INDEX])
            tags.append(ch_info[CH_LANG_INDEX])

        except DBException as err:
            LOG.debug(err)

        return " ".join(tags)

    @staticmethod
    def _tag_match(list_a, list_b):
        """
        Takes in two lists and evaluates if they have any element common.
        Parameters
        ----------
        list_a
            type: list
            first list to compare
        list_b
            type: list
            second list to compare

        Returns
        -------
        type: bool
        true if list matches, false otherwise

        """
        for item in list_a:
            if item in list_b:
                return True
        return False

    def _get_name(self):
        """
        Returns
        -------
        type: str
        file name without extension from an absolute path

        """
        filename = os.path.basename(self.addr)
        filename_without_extension = os.path.splitext(filename)[0]
        return filename_without_extension

    @staticmethod
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
        cmd = "{path_ffprobe} -v quiet -print_format json -show_streams '{path_to_file}'".format(
            path_ffprobe=path_ffprobe,
            path_to_file=path_to_file
        )
        try:
            raw_json = subprocess.check_output(cmd, shell=True).decode('utf-8')
            lang_data = json.loads(raw_json)
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
