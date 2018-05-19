"""
Manages all the database operations
"""
import os
from contextlib import contextmanager
from logging import getLogger
import sqlite3
from sqlite3 import Error
from .custom_exceptions import DBException
from . import __nephos_dir__

LOG = getLogger(__name__)
DB_PATH = os.path.join(__nephos_dir__, "databases/storage.db")


class DBHandler:
    """
    Handles operations related to database; insertion, updating and deletion.
    """

    def first_time(self):
        """
        Initialise the database with important tables
            Channels:
                Stores the list of channels

        Returns
        -------

        """
        LOG.info("Initialising database at %s", DB_PATH)

        with self.connect() as db_cur:

            # create channels and share_list table
            # multiple values to be separated by space. Eg. "AUS IND" for AUS and IND
            # country channels to be shared
            db_cur.execute(""" CREATE TABLE channels (
                                    channel_id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    ip text NOT NULL,
                                    country_code text,
                                    lang text,
                                    timezone text NOT NULL,
                                    status text DEFAULT "up"
                                    );
                                        
                                CREATE TABLE share_list (
                                    share_id integer PRIMARY KEY,
                                    email text,
                                    channel_name text,
                                    country_code text,
                                    lang text,
                                    timezone text,
                                    FOREIGN KEY (channel_name) REFERENCES channels(name)
                                    );
            """)

            # indexing columns
            db_cur.execute(""" CREATE UNIQUE INDEX indexed_name ON channels(
                                    name
                                    );
                                CREATE UNIQUE INDEX indexed_email ON share_list(
                                    email
                                    );                                
            """)

    @staticmethod
    def insert_data(db_cur, table_name, data):
        """
        Inserts data into tables

        Parameters
        ----------
        db_cur
            cursor to database
        table_name
            type: str
            name of the table to which the data is to be inserted
        data
            type: tuple
            containing the comma separated row data to be appended

        Returns
        -------
        id
            type: int
            the channel_id/share_id of the new data

        """
        try:
            command = """ INSERT INTO {table_name}
                            VALUES """.format(table_name=table_name)
            db_cur.execute(command, data)
            return db_cur.lastrowid
        except Error as err:
            LOG.warning("Failed to insert %s into %s", data, table_name)
            LOG.debug(err)

    # TODO: add functions to retrieve data

    @staticmethod
    @contextmanager
    def connect():
        """
        Instantiates the class with a connection to the main database which stores

        Provides cursor to the database connection.

        """
        try:
            conn = sqlite3.connect(DB_PATH)
            yield conn.cursor()
            conn.close()
        except Error as error:
            LOG.warning("Unable to connect to database!\nPlease look into debugging details.")
            LOG.debug(error)
            # catch this exception only if the error can be ignored.
            raise DBException("Database Operation failed!")
