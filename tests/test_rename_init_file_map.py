import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from rename import *
from .stubs import *
from . import TEST_RENAME_INIT_FILEMAP_METADATA, TEST_RENAME_INIT_FILEMAP_ALT


class TestRenameInitFileMapMetadata():
    """
    Tests for function init_file_map() are in this class.
    """
    skiptests = not TEST_RENAME_INIT_FILEMAP_METADATA

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('rename.FileMap')
    @patch('rename.re')
    @patch('rename.os.listdir')
    def test_init_file_map_orthodox(
            self, mock_listdir, mock_re, mock_filemap):
        """
        Tests init_file_map() list building. Verifies expected return value.
        """
        import pdb; pdb.set_trace()
        test_file_map = StubFileMap()
        mock_filemap.return_value = test_file_map
        mock_listdir.return_value = ['/foo/bar']
        mock_re.search.return_value = True
        file_map = init_file_map('.')
        assert file_map.file_map == [
                test_file_map, test_file_map, test_file_map, test_file_map,
                test_file_map, test_file_map]

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.FileMap')
    @patch('rename.re')
    @patch('rename.os')
    def test_init_file_map_with_directories(
            self, mock_os, mock_re, mock_filemap):
        """
        Tests init_file_map() with exception handling. Test exception raised
        when append to file_map list. Verify expected file_map returned.
        """
        mock_os.listdir.return_value = ['/foo/bar']
        mock_os.path.isdir.return_value = True
        mock_re.search.return_value = True
        file_map = init_file_map('.')
        assert file_map.file_map == []

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.FileMap')
    @patch('rename.re')
    @patch('rename.os.listdir')
    def test_init_file_map_raises_exception(
            self, mock_listdir, mock_re, mock_filemap):
        """
        Tests init_file_map() with exception handling. Test exception raised
        when append to file_map list. Verify expected file_map returned.
        """
        mock_filemap.side_effect = Exception("Just testing.")
        mock_listdir.return_value = ['/foo/bar']
        mock_re.search.return_value = True
        file_map = init_file_map('.')
        assert file_map.file_map == []


class Stub2FileMap(object):

    def __init__(self, old_fn, image_type, avoid_collisions=None,
            metadata=None, new_fn=None):
        self.old_fn_fq = old_fn
        self.old_fn = os.path.basename(old_fn)
        self.image_type = image_type

        if avoid_collisions is None:
            self.avoid_collisions = False
        else:
            self.avoid_collisions = avoid_collisions

        if not new_fn:
            if metadata is None:
                self.metadata = {}
            else:
                self.metadata = metadata
            new_fn = "filename.jpg"

        self.new_fn = new_fn


class TestRenameInitFileMapAlt(object):
    """
    Tests using alternate file map.
    """
    skiptests = not TEST_RENAME_INIT_FILEMAP_ALT

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.FileMap', Stub2FileMap)
    @patch('rename.read_alt_file_map')
    @patch('rename.os.listdir')
    def test_basic_alt_map(self, m_listdir, m_readfm):
        """
        """
        expected = ["abc.jpg", "ghi.png"]
        m_readfm.return_value = {"abc": "123", "def": "456", "ghi": "789"}
        m_listdir.return_value = ["abc.jpg", "ghi.png", "jkl.tif"]
        file_map = init_file_map('.', mapfile="mapfile.txt")
        assert len([x for x in file_map.get()]) == len(expected)
        assert file_map.file_map[0].old_fn in expected
        assert file_map.file_map[1].old_fn in expected

