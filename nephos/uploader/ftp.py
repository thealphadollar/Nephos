"""
Handles uploads to FTP server
"""
import os
import ftplib
import ntpath
from logging import getLogger
from pydash import get

from . import get_uploader_config
from ..exceptions import FTPFailure
from ..manage_db import TSK_STORE_INDEX
from ..mail_notifier import add_to_report


LOG = getLogger(__name__)


class FTPUploader:
    """
    A separate uploader from cloud account that uses FTP details to upload
    processed recordings.
    """

    def __init__(self, tasks_list):
        """
        initialises the uploading pipeline, called from within cloud storage uploader

        Parameters
        ----------
        tasks_list
            type:  list
            list containing details of recordings to be uploaded.

        """
        host, port, username, password = self._get_ftp_config()
        if not ((host is None) or (port is None) or
                (username is None) or (password is None)):
            try:
                self.ftp = ftplib.FTP()
                self._auth(host, port, username, password)
                self.nephos_ftp_path = self._create_folder("Nephos")
                self.ftp.cwd(self.nephos_ftp_path)
                for task in tasks_list:
                    self._upload(task[TSK_STORE_INDEX])
                    add_to_report("{folder} successfully uploaded to FTP server.".format(
                        folder=task[TSK_STORE_INDEX]
                    ))
            except FTPFailure as _:
                pass
        else:
            msg = "FTP upload aborted due to incomplete configuration!"
            add_to_report(msg)
            LOG.warning(msg)

    def _upload(self, folder):
        """
        Uploads the given folder to connected FTP server

        Parameters
        ----------
        folder
            type: str
            absolute path to the folder to be uploaded

        Returns
        -------
        type: bool
        True if upload was successful, False otherwise

        """
        upload_to_folder = self._create_folder(self._get_name(folder))
        if upload_to_folder:
            to_path = self.nephos_ftp_path + upload_to_folder
            files = [os.path.join(folder, x) for x in os.listdir(folder)]
            try:
                files.remove(os.path.join(folder, 'ffmpeg2pass-0.log.mbtree'))
            except ValueError:
                pass

            for file in files:
                to_path = to_path + "/" + self._get_name(file)
                with open(file, "rb") as open_file:
                    self.ftp.storbinary("STOR {}".format(to_path), open_file)
                LOG.debug("%s uploaded to %s on FTP server", file, to_path)

    def _auth(self, host, port, username, password):
        """
        Authenticates with the FTP server

        Parameters
        ----------
        host
            type: str
            ftp server hostname
        port
            type: int
            ftp server port
        username
            type: str
            ftp login username
        password
            type: str
            ftp login password

        Returns
        -------
        type: bool
        True is authentication success, False otherwise

        """
        try:
            self.ftp.connect(host, port)
        except ConnectionError as err:
            msg = "couldn't establish connection to ftp server"
            add_to_report("FTP Upload failed: {msg}".format(msg=msg))
            LOG.error(msg)
            LOG.debug(err)
            raise FTPFailure
        LOG.debug("Connection to FTP (host: %s, port: %s) established, "
                  "trying to authenticate...", host, port)

        try:
            self.ftp.login(username, password)
        except ftplib.error_perm as err:
            msg = "FTP server authentication failed"
            add_to_report("FTP Upload failed: {msg}".format(msg=msg))
            LOG.error(msg)
            LOG.debug(err)
            raise FTPFailure
        LOG.debug("Authenticated to FTP server successfully")

    def _create_folder(self, folder_name):
        """
        creates a new folder if it doesn't exist

        Parameters
        -------
        folder_name
            type: str
            name of the folder to be created

        Returns
        -------
        folder_path
            type: str
            path to the create/existing folder
        """
        try:
            self.ftp.mkd(folder_name)
            LOG.debug("%s folder created on FTP server", folder_name)
        except ftplib.error_perm as _:
            LOG.debug("%s folder exists", folder_name)
            if folder_name != "Nephos":
                return ""

        return "/" + folder_name

    @staticmethod
    def _get_ftp_config():
        """
        calls the get_uploader_config method and grabs all ftp config from modules.yaml

        Returns
        -------
        host
            type: str
            ftp server hostname
        port
            type: int
            ftp server port
        username
            type: str
            ftp login username
        password
            type: str
            ftp login password
        """
        config = get_uploader_config()

        base_query = 'upload.ftp.'

        host = get(config, base_query+'host')
        if host is None:
            return host, None, None, None
        port = int(get(config, base_query+'port'))
        username = get(config, base_query+'username')
        password = get(config, base_query+'password')

        return host, port, username, password

    @staticmethod
    def _get_name(path):
        """
        Parses name from the absolute path.

        Parameters
        ----------
        path
            type: str
            absolute path to the file

        Returns
        ---------
            type: str
            name of the folder or file with extension
        -------

        """
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)  # return tail when file, otherwise head for folder
