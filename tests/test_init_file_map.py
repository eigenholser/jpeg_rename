import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from stubs import *


class TestInitFileMap():
    """
    Tests for function init_file_map() are in this class.
    """

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @patch('photo_rename.FileMap')
    @patch('photo_rename.glob')
    def test_init_file_map_orthodox(self, mock_glob, mock_filemap):
        """
        Tests init_file_map() list building. Verifies expected return value.
        """
        test_file_map = StubFileMap()
        mock_filemap.return_value = test_file_map
        mock_glob.glob.return_value = ['/foo/bar']
        file_map = init_file_map('.')
        assert file_map.file_map == [
                test_file_map, test_file_map, test_file_map, test_file_map, test_file_map]

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @patch('photo_rename.FileMap')
    @patch('photo_rename.glob')
    def test_init_file_map_raises_exception(self, mock_glob, mock_filemap):
        """
        Tests init_file_map() with exception handling. Test exception raised
        when append to file_map list. Verify expected file_map returned.
        """
        mock_filemap.side_effect = Exception("Just testing.")
        mock_glob.glob.return_value = ['/foo/bar']
        file_map = init_file_map('.')
        assert file_map.file_map == []
