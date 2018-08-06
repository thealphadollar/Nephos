from unittest import TestCase, mock

from nephos.preprocessor.preprocess import PreprocessHandler, DBException


@mock.patch('nephos.preprocessor.preprocess.PreprocessHandler')
@mock.patch('nephos.preprocessor.preprocess.LOG')
class TestPreprocessHandler(TestCase):

    def test___init__(self, mock_log, mock_preprocess):
        PreprocessHandler.__init__(mock_preprocess, mock.ANY)
        self.assertFalse(mock_log.warning.called)

    @mock.patch('nephos.preprocessor.preprocess.ApplyProcessMethods')
    def test_init_preprocess_pipe(self, mock_methods, mock_log, mock_preprocess):
        mock_preprocess._query_tasks.return_value = ['mocktask']
        PreprocessHandler.init_preprocess_pipe()

        self.assertTrue(mock_preprocess._query_tasks.called)
        self.assertTrue(mock_methods.called)
        self.assertFalse(mock_log.warning.called)

    @mock.patch('nephos.preprocessor.preprocess.DBHandler')
    @mock.patch('nephos.preprocessor.preprocess.ApplyProcessMethods')
    @mock.patch('nephos.preprocessor.preprocess.os')
    def test_insert_task(self, mock_os, mock_methods, mock_db, mock_log, mock_preprocess):
        mock_methods.get_lang.return_value = "test", "test"
        mock_db.insert_data.return_value = "test"
        PreprocessHandler.insert_task("test", "test2")

        self.assertTrue(mock_db.connect.called)
        self.assertTrue(mock_db.insert_data.called)
        self.assertTrue(mock_preprocess._get_channel_name.called)
        self.assertTrue(mock_os.path.join.called)
        self.assertTrue(mock_methods.get_lang.called)
        self.assertTrue(mock_log.debug.called)

    def test_display_tasks(self, mock_log, mock_preprocess):
        mock_preprocess._query_tasks.return_value = ['test task']
        PreprocessHandler.display_tasks()

        self.assertTrue(mock_preprocess._query_tasks.called)
        self.assertTrue(mock_log.info.called)

    def test_add_to_scheduler(self, mock_log, mock_preprocess):
        PreprocessHandler.add_to_scheduler(mock_preprocess)

        self.assertFalse(mock_preprocess.init_preprocess_pipe.called)
        self.assertTrue(mock_log.debug.called)
        self.assertTrue(mock_preprocess.scheduler.add_necessary_job.called)

    @mock.patch('nephos.preprocessor.preprocess.DBHandler')
    def test__query_tasks(self, mock_db, mock_log, _):
        PreprocessHandler._query_tasks("test cmd")

        self.assertTrue(mock_db.connect.called)
        self.assertFalse(mock_log.warning.called)

    @mock.patch('nephos.preprocessor.preprocess.DBHandler')
    def test__query_tasks_fail(self, mock_db, mock_log, _):
        mock_db.connect.side_effect = DBException()
        PreprocessHandler._query_tasks("test cmd")

        self.assertTrue(mock_db.connect.called)
        self.assertTrue(mock_log.warning.called)

    @mock.patch('nephos.preprocessor.preprocess.DBHandler')
    def test__get_channel_name(self, mock_db, _, __):
        PreprocessHandler._get_channel_name("test", mock_db)

        self.assertTrue(mock_db.execute.called)
        self.assertTrue(mock_db.fetchall.called)
