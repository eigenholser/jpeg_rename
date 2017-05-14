import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

import photo_rename
from photo_rename.rename import *
from .stubs import *
from . import (
    TEST_HARVESTER_INIT_FILEMAP_METADATA, TEST_HARVESTER_INIT_FILEMAP_ALT,
    TEST_HARVESTER_FILES_FROM_DIRECTORY)


class TestRenameInitFilemapMetadata():
    """
    Tests for function init_file_map() are in this class.
    """
    skiptests = not TEST_HARVESTER_INIT_FILEMAP_METADATA

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.Filemap')
    def test_init_file_map_orthodox(self, m_filemap):
        """
        Tests init_file_map() list building from directory. Code cares about
        capitalization of filenames. Verifies expected return value.
        """
        test_file_map = StubFilemap()
        m_filemap.return_value = test_file_map
        harvey = Harvester(".")
        harvey.files = ['abc.jpg', '123.JPG']
        filemaps = [fm for fm in harvey["filemaps"].get()]
        assert filemaps == [test_file_map, test_file_map]

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.Filemap')
    @patch('photo_rename.harvester.re')
    @patch('photo_rename.harvester.os')
    def test_init_file_map_with_directories(self, m_os, m_re, m_filemap):
        """
        Tests init_file_map() with exception handling. Test exception raised
        when append to file_map list. Verify expected file_map returned.
        """
        m_os.listdir.return_value = ['/foo/bar']
        m_os.path.isdir.return_value = True
        m_re.search.return_value = True
        harvey = Harvester(".")
        filemaps = [fm for fm in harvey["filemaps"].get()]
        assert filemaps == []

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.Filemap')
    @patch('photo_rename.harvester.re')
    @patch('photo_rename.harvester.os.listdir')
    def test_init_file_map_raises_exception(self, m_listdir, m_re, m_filemap):
        """
        Tests init_file_map() with exception handling. Test exception raised
        when append to file_map list. Verify expected file_map returned.
        """
        m_filemap.side_effect = Exception("Just testing.")
        m_listdir.return_value = ['/foo/bar']
        m_re.search.return_value = True
        harvey = Harvester(".")
        filemaps = [fm for fm in harvey["filemaps"].get()]
        assert filemaps == []


class Stub2Filemap(object):

    def __init__(self, src_fn, image_type, metadata=None, dst_fn=None,
            read_metadata=False):
        self.src_fn_fq = src_fn
        self.src_fn = os.path.basename(src_fn)
        self.image_type = image_type

        if not dst_fn:
            if metadata is None:
                self.metadata = {}
            else:
                self.metadata = metadata
            dst_fn = "filename.jpg"

        self.dst_fn = dst_fn


class TestRenameInitFilemapAlt(object):
    """
    Tests using alternate file map.
    """
    skiptests = not TEST_HARVESTER_INIT_FILEMAP_ALT

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.Filemap', Stub2Filemap)
    @patch('photo_rename.Harvester.read_alt_file_map')
    @patch('photo_rename.harvester.os.listdir')
    def test_basic_alt_map(self, m_listdir, m_readfm):
        """
        Test happy path against alternate file map.
        """
        expected = ["abc.jpg", "ghi.png"]
        m_readfm.return_value = {"abc": "123", "def": "456", "ghi": "789"}
        m_listdir.return_value = ["abc.jpg", "ghi.png", "jkl.tif"]
        harvey = Harvester(".", mapfile="mapfile.txt")
        filemaps = [fm for fm in harvey["filemaps"].get()]
        assert len(filemaps) == len(expected)
        assert filemaps[0].src_fn in expected
        assert filemaps[1].src_fn in expected


class TestFilesFromDirectory(object):
    """
    Tests for Harvester.filees_from_directory() method.
    """
    skiptests = not TEST_HARVESTER_FILES_FROM_DIRECTORY

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.FileList')
    @patch('photo_rename.harvester.os.listdir')
    @patch('photo_rename.harvester.os.path.splitext')
    def test_files_from_directory_happy(self, m_splitext, m_listdir, m_filelist):
        """
        Test files_from_directory() with list of files, one of which matches a
        recognized image extension 'xyz'. Confirm only file with recognized
        extension returned.
        """
        files = ['12.jpg', '34.png', '56.arw', '78.tif', '90.xyz']
        m_splitext.return_value = ('ABC', '.XYZ')
        m_listdir.return_value = files
        attrs = {'get.return_value': files}
        m_get = Mock()
        m_get.configure_mock(**attrs)
        m_filelist.return_value = m_get
        harvey = Harvester('.')
        actual_files = harvey.files_from_directory(".")
        assert files[4] == actual_files[4]

