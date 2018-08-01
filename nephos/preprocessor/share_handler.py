"""
Class and methods required to handle sharing
"""
from logging import getLogger
from sqlite3 import Error

from .. import validate_entries
from ..manage_db import DBHandler, DBException


LOG = getLogger(__name__)
CMD_GET_SHRS = "SELECT * FROM share_list"
CMD_DEL_SHRS = "DELETE FROM share_list"


class ShareHandler:
    """
    Class to manage all operations related to share lists
    """
    def add_share_entity(self):
        """
        Provides CLI to add a single share job

        Returns
        -------

        """
        email = input("Email: ").lower()
        tags = input("Tags [channel names, languages, timezone, country code] "
                     "(multi entries separated by space): ").lower()

        shr_data = {
            0: {
                "email": email,
                "tags": tags
            }
        }
        self.insert_share_entities(shr_data)

    @staticmethod
    def insert_share_entities(shr_data):
        """
        Adds channels to the database

        Parameters
        ----------
        shr_data
            type: dict
            dict of share entities' data to be appended to the share_list table

        Returns
        -------

        """
        shr_data = validate_entries("share-entity", shr_data)
        for key in shr_data.keys():
            try:
                with DBHandler.connect() as db_cur:
                    shr_id = DBHandler.insert_data(db_cur, "share_list", shr_data[key])
                LOG.info("Share entity (id = %s) added with following data:\n%s", shr_id,
                         shr_data[key])
            except DBException as err:
                LOG.info("Failed to connect to database")
                LOG.debug(err)

    def display_shr_entities(self):
        """
        Displays list of share entities currently stored in the database

        Returns
        -------

        """
        shr_entities = self.grab_shr_list()
        LOG.info("\nid\temail\t\ttags")
        for entity in shr_entities:
            print("\t".join(str(x) for x in entity))

    @staticmethod
    def delete_entity():
        """
        Deletes share entity from the database

        Returns
        -------

        """
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(CMD_DEL_SHRS)
            LOG.info("Sharing list cleaned to add new data...")
        except (Error, DBException) as err:
            LOG.warning("Failed to remove share lists!")
            LOG.debug(err)
            raise IOError

    @staticmethod
    def grab_shr_list():
        """
        Extracts the table of currently stored channels

        Returns
        -------
        type: tuple
        tuple containing column values for all the channels

        """
        try:
            with DBHandler.connect() as db_cur:
                db_cur.execute(CMD_GET_SHRS)
                shr_list = db_cur.fetchall()
            return shr_list
        except DBException as err:
            LOG.warning("Failed to get share_entities list!")
            LOG.debug(err)
