"""
Derived class from uploader which manages uploading to Google Drive account.
"""
import os
from logging import getLogger
from googleapiclient.http import HttpError, MediaFileUpload, UnexpectedMethodError, \
    ResumableUploadError, UnexpectedBodyError
from googleapiclient import discovery
from google.oauth2 import service_account
from .uploader import Uploader
from ..exceptions import OAuthFailure, UploadingFailed
from ..manage_db import DBHandler


LOG = getLogger(__name__)
SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_KEY_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".nephos-key")


class GDrive(Uploader):

    def auth(self):
        """
        Runs authentication pipeline.

        Returns
        -------

        """
        try:
            credentials = service_account.Credentials.from_service_account_file(SERVICE_KEY_PATH,
                                                                                scopes=SCOPES)
            LOG.info("Drive API authenticated using service account credentials!")
        except service_account.Credentials.expired:
            raise OAuthFailure

        try:
            self.service = discovery.build("drive", "v3", credentials=credentials,
                                           cache_discovery=False)
            LOG.info("Drive API authenticated using service account credentials!")
        except HttpError as error:
            LOG.error("Authentication request failed!")
            LOG.debug(error)
            raise OAuthFailure

    @staticmethod
    def _get_upload_service():
        """
        Returns
        -------
        file_upload_service
            type: googleapiclient.discovery.build
            service to handle uploading and adding permissions for user
        """
        credentials = service_account.Credentials.from_service_account_file(SERVICE_KEY_PATH,
                                                                            scopes=SCOPES)
        return discovery.build("drive", "v3", credentials=credentials, cache_discovery=False)

    @staticmethod
    def _upload(folder, share_list):
        """
        Uploads the folder and appends share entities

        Parameters
        -------
        folder
            type: str
            path to folder to be uploaded
        share_list
            type: str
            str of entities the file is to be shared with,
            multiple values separated by space

        Returns
        -------

        """
        service = GDrive._get_upload_service()
        file_service = service.files()
        permissions_service = service.permissions()
        batch_service = service.new_batch_http_request(callback=GDrive._share_callback)
        try:
            try:
                GDrive._set_uploading(folder)
                folder_id = GDrive._create_folder(file_service, folder)
                GDrive._upload_files(file_service, folder, folder_id)
                GDrive._share(batch_service, permissions_service, folder_id, share_list)
                GDrive._remove(folder)
                LOG.debug("%s uploaded successfully!", folder)
            except (UnexpectedBodyError, ResumableUploadError, UnexpectedMethodError,
                    HttpError) as error:
                LOG.warning("Uploading %s failed! Will retry later", folder)
                LOG.debug(error)
                with DBHandler.connect() as db_cur:
                    raise UploadingFailed(folder, db_cur)
        except UploadingFailed:
            pass

    @staticmethod
    def _create_folder(file_service, folder):
        """
        Creates the folder to upload the recording to.
        Parameters
        ----------
        file_service
            file managing service for google drive
        folder
            type: str
            folder to the uploaded

        Returns
        -------

        """
        file_metadata = {
            'name': GDrive._get_name(folder),
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder_id = file_service.create(
            body=file_metadata,
            fields='id'
        ).execute().get('id')
        LOG.debug("%s folder created, id: %s", folder, folder_id)
        return folder_id

    @staticmethod
    def _upload_files(file_service, folder, folder_id):
        """
        uploads files present in the folder to google drive under
        the provided folder's id.

        Parameters
        ----------
        file_service
            file managing service for google drive
        folder
            type: str
            absolute path of folder to be uploaded
        folder_id
            type: str
            unique folder id of the cloud parent folder

        Returns
        -------

        """
        files = [os.path.join(folder, x) for x in os.listdir(folder)]
        try:
            files.remove(os.path.join(folder, 'ffmpeg2pass-0.log.mbtree'))
        except ValueError:
            pass
        for file_path in files:
            file_metadata = {
                'name': GDrive._get_name(file_path),
                'parents': [folder_id]
            }
            media = MediaFileUpload(
                file_path,
                mimetype=GDrive._get_mimetype(GDrive._get_name(file_path)),
                resumable=True
            )
            file_id = file_service.create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute().get('id')
            LOG.debug("%s uploaded to file ID: %s", file_path, file_id)

    @staticmethod
    def _share(batch_service, perm_service, folder_id, share_list):
        """
        Share a given folderid with some other entity.
        Role defines the level of access the entity can have.
        The supported values for role are: owner, reader, writer or commenter.

        Currently we add everyone as reader.

        Parameters
        ----------
        batch_service
            batch http requests managing service for google drive
        perm_service
            permissions managing service for google drive
        folder_id
            type: str
            unique folder id of the cloud folder
        share_list
            type: str
            str of entities the file is to be shared with,
            multiple values separated by space

        Returns
        -------

        """
        for email in share_list.split():
            permission = {
                "type": "user",
                "role": "reader",
                "emailAddress": email
            }
            batch_service.add(perm_service.create(
                fileid=folder_id,
                body=permission,
                fields='id',
            ))

        batch_service.execute()

    @staticmethod
    def _get_mimetype(filename):
        """
        https://developers.google.com/drive/api/v3/mime-types

        Parameters
        ----------
        filename
            type: str
            name of the file

        Returns
        -------
        mimeType
            type: str
            google drive mimetype

        """
        name_parts = filename.split('.')
        extension = name_parts[len(name_parts)-1]

        mimetype = {
            "mp4": 'video/mp4',
            "txt": 'text/plain',
            "srt": 'text/plain',
            "log": 'text/plain'
        }

        return mimetype[extension]

    @staticmethod
    def _share_callback(request_id, response, exception):
        if exception:
            # Handle error
            LOG.debug(exception)
        else:
            LOG.debug("Permission Id: %s", response.get('id'))

