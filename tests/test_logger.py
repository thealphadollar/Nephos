from unittest import TestCase, mock
import os
import tempfile
from nephos.logger import EnsureFolderFileHandler


class TestEnsureFolderFileHandler(TestCase):

    @mock.patch('logging.FileHandler.__init__')
    def test_directory_made(self, mock_logging):
        with tempfile.TemporaryDirectory() as temp_dir:
            file = os.path.join(temp_dir, "dir/file.txt")
            dir_name = os.path.dirname(file)
            EnsureFolderFileHandler(file)

            self.assertTrue(os.path.exists(dir_name))
            self.assertTrue(mock_logging.called)
