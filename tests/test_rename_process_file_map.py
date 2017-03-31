import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from rename import *
from .stubs import *
from . import TEST_RENAME_PROCESS_FILEMAP


class TestRenameProcessFilemap(object):
    """
    Tests for function process_file_map() are in this class.
    """
    skiptests = not TEST_RENAME_PROCESS_FILEMAP

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    def test_process_file_map(self):
        """Test process_file_map()."""
        def move_func(old_fn, new_fn):
            pass

        file_map_list = FileMapList()
        file_map_list.add(StubFileMap())
        assert process_file_map(file_map_list, True, move_func) == None

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    def test_process_file_map_raise_exception(self):
        """Test exception handling in process_file_map()."""
        def move_func(old_fn, new_fn):
            raise Exception("Faux failure")
        file_map_list = FileMapList()
        file_map_list.add(StubFileMap())
        assert process_file_map(file_map_list, True, move_func) == None

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.FileMap')
    def test_process_file_map_simon_sez_false_fn_eq(self, mock_fm):
        """Test process_file_map() with simon_sez=False. Tests else branch with
        old_fn == new_fn. Verify same_files attribute value is True."""
        mock_fm.same_files = True
        mock_fm.old_fn = OLD_FN_JPG_LOWER
        mock_fm.new_fn = OLD_FN_JPG_LOWER
        file_map_list = FileMapList()
        file_map_list.add(mock_fm)
        process_file_map(file_map_list)
        assert mock_fm.same_files == True

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.FileMap')
    def test_process_file_map_simon_sez_false_fn_ne(self, mock_fm):
        """Test process_file_map() with simon_sez=False. Tests else branch with
        old_fn != new_fn. Verify same_files attribute value is False."""
        mock_fm.same_files = False
        mock_fm.old_fn = OLD_FN_JPG_LOWER
        mock_fm.new_fn = ''
        file_map_list = FileMapList()
        file_map_list.add(mock_fm)
        process_file_map(file_map_list)
        assert mock_fm.same_files == False

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.FileMap.move')
    @patch('photo_rename.FileMap')
    def test_process_file_map_simon_sez(self, mock_fm, mock_fm_move):
        """Call process_file_map with simon_sez=True, move_func=None. Tests
        call to move() method of FileMap instance when no test stub present and
        simon_sez True. Verify call to move() made as expected."""
        file_map_list = FileMapList()
        file_map_list.add(mock_fm)
        process_file_map(file_map_list, simon_sez=True)
        mock_fm.move.assert_called_with()
