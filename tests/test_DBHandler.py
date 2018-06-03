from unittest import TestCase, mock
import tempfile
import os
from nephos.manage_db import DBHandler, DBException

temp_dir = tempfile.TemporaryDirectory()
DB_PATH = os.path.join(temp_dir.name, "storage.db")
DB_JOBS_PATH = os.path.join(temp_dir.name, "jobs.db")


class TestDBHandler(TestCase):

    db_handler = DBHandler()

    @mock.patch('nephos.manage_db.DB_PATH', new=DB_PATH)
    @mock.patch('nephos.manage_db.DBHandler.connect')
    def test_first_time(self, mock_connect):
        with mock.patch('nephos.manage_db.LOG') as mock_log:
            self.db_handler.first_time()

            mock_log.info.assert_called_with("Initialising database at %s", DB_PATH)
            self.assertTrue(mock_connect.called)

#     def test_insert_data(self):
#         self.fail()
#
#     def test_init_jobs_db(self):
#         self.fail()
#

    @mock.patch('nephos.manage_db.DB_PATH', new=temp_dir.name)
    def test_connect_db(self):
        with self.failUnlessRaises(DBException):
            with self.db_handler.connect():
                pass
