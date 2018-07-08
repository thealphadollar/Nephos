"""
Derived class from uploader which manages uploading to Google Drive account.
"""
import os
from logging import getLogger
from oauth2client import client, file
from oauth2client.clientsecrets import InvalidClientSecretsError
from googleapiclient.http import HttpError, MediaFileUpload, UnexpectedMethodError, \
    ResumableUploadError, UnexpectedBodyError
from googleapiclient import discovery
from httplib2 import Http
from .uploader import Uploader
from .. import __nephos_dir__
from ..exceptions import OAuthFailure, UploadingFailed
from ..manage_db import DBHandler


LOG = getLogger(__name__)
SCOPES = "https://www.googleapis.com/auth/drive"
APPLICATION_NAME = "Project Nephos"
CRED_PATH = os.path.join(__nephos_dir__, ".up_cred")
CLI_SECRET_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".client_secrets")


class GDrive(Uploader):

    def auth(self):
        """
        Runs authentication pipeline.

        Returns
        -------

        """
        store = file.Storage(CRED_PATH)
        try:
            credentials = self._auth_from_file(store)
            LOG.info("Drive API authenticated using saved credentials!")
        except OAuthFailure:
            credentials = self._init_auth_flow()

        store.put(credentials)

        try:
            http = credentials.authorize(Http())
            self.service = discovery.build("drive", "v3", http=http, cache_discovery=False)
            LOG.info("Authenticated successfully!")
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
        http = GDrive._auth_from_file(file.Storage(CRED_PATH)).authorize(Http())
        return discovery.build("drive", "v3", http=http, cache_discovery=False)

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
        try:
            try:
                GDrive._set_uploading(folder)
                folder_id = GDrive._create_folder(file_service, folder)
                GDrive._upload_files(file_service, folder, folder_id)
                GDrive._share(permissions_service, folder_id, share_list)
                GDrive._remove(folder)
                LOG.debug("%s uploaded successfully!")
            except (UnexpectedBodyError, ResumableUploadError, UnexpectedMethodError,
                    HttpError) as error:
                LOG.warning("Uploading %s failed! Will retry later", folder)
                LOG.debug(error)
                with DBHandler.connect() as db_cur:
                    raise UploadingFailed(folder, db_cur)
        except UploadingFailed:
            pass

    @staticmethod
    def _auth_from_file(store):
        """
        Uses the stored credentials to authenticate.

        Parameters
        -------
        store
            type: oauth2client.file.Storage
            link to the file containing credentials

        Returns
        -------
        credentials
            type: Oauth2Credentials
            Auth credentials stored in the file.
        """
        credentials = store.get()

        def raise_error():
            LOG.warning("Authentication using credentials file failed!")
            raise OAuthFailure

        if not credentials:
            raise_error()
        elif credentials.invalid:
            raise_error()

        return credentials

    @staticmethod
    def _init_auth_flow():
        """
        Authenticates with the google account via OAuth2.

        Runs at the first start of Nephos, and stores the authentication in a file. If the
        file is somehow tampered, this authentication method will be called again.

        Returns
        -------
        credentials
            type: OAuth2Credentials
            The credentials after the flow is successful.
        """

        try:
            flow = client.flow_from_clientsecrets(
                filename=CLI_SECRET_PATH,
                scope=SCOPES,
                redirect_uri="urn:ietf:wg:oauth:2.0:oob"  # GUI is not opened
            )
        except (InvalidClientSecretsError, ValueError) as error:
            LOG.error("Invalid client secrets file provided at {filepath}".format(
                filepath=CLI_SECRET_PATH
            ))
            LOG.debug(error)
            raise OAuthFailure()

        flow.user_agent = APPLICATION_NAME
        url = flow.step1_get_authorize_url()

        LOG.info("Please visit the following URL: {auth_url}".format(
            auth_url=url
        ))
        code = input("Enter the code: ")

        try:
            credentials = flow.step2_exchange(code)
        except client.FlowExchangeError as error:
            LOG.error("Failed to authenticate!")
            LOG.debug(error)
            raise OAuthFailure()
        LOG.info("Authenticated successfully")

        return credentials

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
        LOG.debug("%s folder upload, folder id: %s", folder, folder_id)
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
        files = [os.path.abspath(x) for x in os.listdir(folder)]
        for file_path in files:
            file_metadata = {
                'name': GDrive._get_name(file_path),
                'parents': folder_id
            }
            media = MediaFileUpload(
                file_path,
                mimetype=GDrive._get_mimetype(GDrive._get_name(file)),
                resumable=True
            )
            file_id = file_service.create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute().get('id')
            LOG.debug("%s uploaded to file ID: %s", file_path, file_id)

    @staticmethod
    def _share(perm_service, folder_id, share_list):
        """
        Share a given folderid with some other entity.
        Role defines the level of access the entity can have.
        The supported values for role are: owner, reader, writer or commenter.

        Currently we add everyone as reader.

        Parameters
        ----------
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
            perm_metadata = perm_service.create(
                fileid=folder_id,
                body=permission
            ).execute()

            LOG.debug(perm_metadata)

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
            "mp4": 'application/vnd.google-apps.video',
            "txt": 'application/vnd.google-apps.document',
            "srt": 'application/vnd.google-apps.document'
        }

        return mimetype[extension]
