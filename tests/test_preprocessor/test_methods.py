from unittest import mock, TestCase

from nephos.preprocessor.methods import ApplyProcessMethods


class MockPopen:
    def __init__(self, cmd, shell, stdout, stderr):
        pass

    @staticmethod
    def communicate():
        return "some text", "some other text"


class MockSize:
    def __init__(self, _):
        self.st_size = 2018


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


mock_lang_data = {
    "streams":
    [

        {
            "codec_type": "audio",
            "tags": {
                "language": "eng"
            }
        },
        {
            "codec_type": "subtitle",
            "tags": {
                "language": "spa"
            }
         }
    ]
}

mock_share_list = {
    'entry': "test"
}


@mock.patch('nephos.preprocessor.methods.ApplyProcessMethods')
@mock.patch('nephos.preprocessor.methods.LOG')
class TestApplyProcessMethods(TestCase):

    @mock.patch('nephos.preprocessor.methods.DBHandler')
    def test___init__(self, mock_db, mock_log, mock_methods):
        ApplyProcessMethods.__init__(mock_methods, 'test', 'test')

        self.assertTrue(mock_methods._get_name.called)
        self.assertTrue(mock_db.connect.called)
        self.assertTrue(mock_methods._apply_methods.called)
        self.assertFalse(mock_log.warning.called)

    @mock.patch('os.remove')
    @mock.patch('os.makedirs')
    @mock.patch('nephos.preprocessor.methods.DBHandler')
    def test__apply_methods(self, mock_db, mock_mkdir, mock_rm, mock_log, mock_methods):
        ApplyProcessMethods._apply_methods(mock_methods)

        self.assertTrue(mock_mkdir.called)
        self.assertTrue(mock_methods._execute_processing.called)
        self.assertTrue(mock_methods._add_share_entities.called)
        self.assertTrue(mock_rm.called)
        self.assertTrue(mock_db.connect.called)
        self.assertFalse(mock_log.debug.called)

    @mock.patch('nephos.preprocessor.methods.subprocess')
    @mock.patch('os.path')
    @mock.patch('os.stat')
    def test__execute_processing(self, mock_stat, mock_path, mock_subprocess, mock_log, mock_methods):
        mock_subprocess.Popen.side_effect = MockPopen
        mock_stat.side_effect = MockSize
        ApplyProcessMethods._execute_processing(mock_methods)

        self.assertTrue(mock_path.join.called)
        self.assertTrue(mock_log.debug.called)
        self.assertTrue(mock_subprocess.Popen.called)
        self.assertTrue(mock_stat.called)

    @mock.patch('nephos.preprocessor.methods.ShareHandler')
    @mock.patch('nephos.preprocessor.methods.DBHandler')
    def test__add_share_entities(self, mock_db, mock_share, mock_log, mock_methods):
        mock_share.grab_shr_list.return_value = mock_share_list
        mock_methods._tag_match.return_value = False
        ApplyProcessMethods._add_share_entities(mock_methods)

        self.assertTrue(mock_share.grab_shr_list.called)
        self.assertTrue(mock_methods._assemble_tags.called)
        self.assertTrue(mock_methods._tag_match.called)
        self.assertTrue(mock_db.connect.called)
        self.assertFalse(mock_log.debug.called)

    @mock.patch('nephos.preprocessor.methods.DBHandler')
    def test__assemble_tags(self, mock_db, mock_log, mock_methods):
        with self.failUnlessRaises(TypeError):
            ApplyProcessMethods._assemble_tags(mock_methods)

        self.assertTrue(mock_db.connect.called)
        self.assertFalse(mock_log.debug.called)

    def test__tag_match_true(self, _, __):
        ls_a = ["text1", "text2"]
        ls_b = ["text2", "text3"]
        return_value = ApplyProcessMethods._tag_match(ls_a, ls_b)

        self.assertTrue(return_value)

    def test__tag_match_false(self, _, __):
        ls_a = ["text1", "text2"]
        ls_b = ["text4", "text3"]
        return_value = ApplyProcessMethods._tag_match(ls_a, ls_b)

        self.assertFalse(return_value)

    def test__get_name(self, _, mock_methods):
        mock_methods.addr = '/home/user/return.txt'
        expected = "return"
        output = ApplyProcessMethods._get_name(mock_methods)

        self.assertEqual(output, expected)

    @mock.patch('nephos.preprocessor.methods.subprocess')
    @mock.patch('nephos.preprocessor.methods.json')
    def test__get_lang(self, mock_json, mock_subprocess, mock_log, _):
        mock_subprocess.check_output.return_value = 'test'.encode()
        mock_json.loads.return_value = HashableDict(mock_lang_data)
        aud_lang, sub_lang = ApplyProcessMethods.get_lang("test")

        self.assertFalse(mock_log.warning.called)
        self.assertTrue(mock_log.debug.called)
        self.assertTrue(mock_subprocess.check_output.called)
        self.assertTrue(mock_json.loads.called)
        self.assertEqual(aud_lang, 'eng')
        self.assertEqual(sub_lang, 'spa')
