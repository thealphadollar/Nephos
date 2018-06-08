from unittest import TestCase, mock
import tempfile
import os
from nephos.manage_db import DBHandler, DBException

TEMP_DIR = tempfile.TemporaryDirectory()
DB_PATH = os.path.join(TEMP_DIR.name, "storage.db")
DB_JOBS_PATH = os.path.join(TEMP_DIR.name, "jobs.db")

MOCK_DATA = {'name': 'abc'}


class TestDBHandler(TestCase):

    db_handler = DBHandler()

    @mock.patch('nephos.manage_db.DB_PATH', new=DB_PATH)
    @mock.patch('nephos.manage_db.LOG')
    @mock.patch('nephos.manage_db.DBHandler.connect')
    def test_first_time(self, mock_connect, mock_log):
        self.db_handler.first_time()

        mock_log.debug.assert_called_with("Initialising database at %s", DB_PATH)
        self.assertTrue(mock_connect.called)

    @mock.patch('nephos.manage_db.DB_PATH', new=DB_PATH)
    @mock.patch('nephos.manage_db.LOG')
    def test_insert_wrong_data(self, mock_log):
        with self.db_handler.connect() as db_cur:
            table_name = "test"
            self.db_handler.insert_data(db_cur, table_name, MOCK_DATA)

            self.assertTrue(mock_log.warning.called)
            self.assertTrue(mock_log.debug.called)

    @mock.patch('nephos.manage_db.DB_JOBS_PATH', new=TEMP_DIR.name)
    def test_wrong_connect_jobs_db(self):
        with self.assertRaises(DBException):
            with self.db_handler.init_jobs_db():
                pass
        TEMP_DIR.cleanup()  # in tests, this is the last to be called from this test module

    @mock.patch('nephos.manage_db.DB_PATH', new=TEMP_DIR.name)
    def test_wrong_connect_channel_db(self):
        with self.assertRaises(DBException):
            with self.db_handler.connect():
                pass
