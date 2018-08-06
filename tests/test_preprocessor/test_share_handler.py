from unittest import TestCase, mock

from nephos.preprocessor.share_handler import ShareHandler, DBException


@mock.patch('nephos.preprocessor.share_handler.ShareHandler')
@mock.patch('nephos.preprocessor.share_handler.LOG')
class TestShareHandler(TestCase):

    @mock.patch('nephos.preprocessor.share_handler.input')
    def test_add_share_entity(self, mock_input, mock_log, mock_share):
        ShareHandler.add_share_entity(mock_share)

        self.assertTrue(mock_input.called)
        self.assertTrue(mock_share.insert_share_entities.called)
        self.assertFalse(mock_log.warning.called)

    @mock.patch('nephos.preprocessor.share_handler.DBHandler')
    @mock.patch('nephos.preprocessor.share_handler.validate_entries')
    def test_insert_share_entities(self, mock_validate, mock_db, mock_log, _):
        mock_validate.return_value = {"test": "text"}
        ShareHandler.insert_share_entities("test")

        self.assertTrue(mock_validate.called)
        self.assertTrue(mock_db.connect.called)
        self.assertTrue(mock_db.insert_data.called)
        self.assertTrue(mock_log.info.called)
        self.assertFalse(mock_log.debug.called)

    @mock.patch('nephos.preprocessor.share_handler.DBHandler')
    @mock.patch('nephos.preprocessor.share_handler.validate_entries')
    def test_insert_share_entities_fails(self, mock_validate, mock_db, mock_log, _):
        mock_validate.return_value = {"test": "text"}
        mock_db.insert_data.side_effect = DBException()
        ShareHandler.insert_share_entities({"test": "text"})

        self.assertTrue(mock_validate.called)
        self.assertTrue(mock_db.connect.called)
        self.assertTrue(mock_db.insert_data.called)
        self.assertTrue(mock_log.info.called)
        self.assertTrue(mock_log.debug.called)

    def test_display_shr_entities(self, mock_log, mock_share):
        ShareHandler.display_shr_entities(mock_share)

        self.assertTrue(mock_share.grab_shr_list.called)
        self.assertTrue(mock_log.info.called)

    @mock.patch('nephos.preprocessor.share_handler.DBHandler')
    def test_delete_entity(self, mock_db, mock_log, _):
        ShareHandler.delete_entity()

        self.assertTrue(mock_db.connect.called)
        self.assertTrue(mock_log.info.called)
        self.assertFalse(mock_log.warning.called)

    @mock.patch('nephos.preprocessor.share_handler.DBHandler')
    def test_delete_entity_fail(self, mock_db, mock_log, _):
        mock_db.connect.side_effect = DBException()
        with self.failUnlessRaises(IOError):
            ShareHandler.delete_entity()

        self.assertTrue(mock_db.connect.called)
        self.assertFalse(mock_log.info.called)
        self.assertTrue(mock_log.warning.called)

    @mock.patch('nephos.preprocessor.share_handler.DBHandler')
    def test_grab_shr_list(self, mock_db, mock_log, _):
        ShareHandler.grab_shr_list()

        self.assertTrue(mock_db.connect.called)
        self.assertFalse(mock_log.warning.called)
        self.assertFalse(mock_log.debug.called)

    @mock.patch('nephos.preprocessor.share_handler.DBHandler')
    def test_grab_shr_list(self, mock_db, mock_log, _):
        mock_db.connect.side_effect = DBException()
        ShareHandler.grab_shr_list()

        self.assertTrue(mock_db.connect.called)
        self.assertTrue(mock_log.warning.called)
        self.assertTrue(mock_log.debug.called)
