import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

import photo_rename
from photo_rename.rename import *
from .stubs import *
from . import TEST_HARVESTER_GETITEM


class TestHarvesterGetItem(object):
    """
    Tests for __getitem__() magic method.
    """
    skiptests = not TEST_HARVESTER_GETITEM

    ##
    ## not filemaps and not metadata_dst_dir
    ##

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.Harvester.init_file_map')
    def test_getitem_filemap_will_initialize(self, m_init_file_map):
        """
        Test get filemaps when it has not yet initialized. Will call
        init_file_map() to build filemap. Mock out init_file_map(). Verify
        init_file_map() called once. Verify correct return value.
        """
        expected_filemaps = 1234
        m_init_file_map.return_value = expected_filemaps # Randome whatever.
        harvey = Harvester('.')
        actual_filemaps = harvey["filemaps"]
        m_init_file_map.assert_called_once()
        assert expected_filemaps == actual_filemaps

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.Harvester.init_file_map')
    def test_getitem_filemap_return_stored(self, m_init_file_map):
        """
        Test get filemaps after it has initialized. Will return existing
        filemaps. Verify init_file_map() not called. Verify correct return
        value.
        """
        expected_filemaps = 1234
        harvey = Harvester('.')
        # Set an existing value so the initialization branch is not taken.
        harvey.filemaps = expected_filemaps
        actual_filemaps = harvey["filemaps"]
        m_init_file_map.assert_not_called()
        assert expected_filemaps == actual_filemaps

    ##
    ## not filemaps and not metadata_dst_dir
    ##

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.Harvester.filemaps_for_metadata_copy')
    def test_getitem_not_filemap_not_md_dst_dir(
            self, m_filemaps_for_metadata_copy):
        """
        Test get filemaps for metadata copy before init.  Verify that
        filemaps_for_metadata_copy() called. Verify correct return value.
        """
        expected_filemaps = 1234
        harvey = Harvester('.', metadata_dst_directory=".")
        # Initialization branch will be taken. Our mock will return value.
        m_filemaps_for_metadata_copy.return_value = expected_filemaps
        actual_filemaps = harvey["filemaps"]
        m_filemaps_for_metadata_copy.assert_called_once()
        assert expected_filemaps == actual_filemaps

    ##
    ## files and mapfile
    ##

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.Harvester.files_from_mapfile')
    def test_getitem_files_mapfile_initialize(self, m_files_from_mapfile):
        """
        Test get files with mapfile before it has initialized. Will call
        files_from_mapfile() to initialize. Verify files_from_mapfile()
        called. Verify correct return value.
        """
        expected_files = 1234
        m_files_from_mapfile.return_value = expected_files
        # Initialize Harvester instance with directory and mapfile.
        harvey = Harvester('.', mapfile="abc")
        actual_files = harvey["files"]
        m_files_from_mapfile.assert_called_once()
        assert expected_files == actual_files

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.Harvester.files_from_mapfile')
    def test_getitem_files_mapfile_return_stored(self, m_files_from_mapfile):
        """
        Test get files with mapfile after it has initialized. Will not call
        files_from_mapfile() to initialize. Verify files_from_mapfile()
        not called. Verify correct return value.
        """
        expected_files = 1234
        # Initialize Harvester instance with directory and mapfile.
        harvey = Harvester('.', mapfile="abc")
        # Set an existing value so the initialization branch is not taken.
        harvey.files = expected_files
        actual_files = harvey["files"]
        m_files_from_mapfile.assert_not_called()
        assert expected_files == actual_files

    ##
    ## files and not mapfile
    ##

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.Harvester.files_from_directory')
    def test_getitem_files_initialize(self, m_files_from_directory):
        """
        Test get files not mapfile before it has initialized. Will call
        files_from_directory() to initialize. Verify files_from_directory()
        called. Verify correct return value.
        """
        expected_files = 1234
        m_files_from_directory.return_value = expected_files
        # Initialize Harvester instance with directory and mapfile.
        harvey = Harvester('.')
        actual_files = harvey["files"]
        m_files_from_directory.assert_called_once()
        assert expected_files == actual_files

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.Harvester.files_from_directory')
    def test_getitem_files_return_stored(self, m_files_from_directory):
        """
        Test get files not mapfile after it has initialized. Will not call
        files_from_directory() to initialize. Verify files_from_directory()
        not called. Verify correct return value.
        """
        expected_files = 1234
        # Initialize Harvester instance with directory and mapfile.
        harvey = Harvester('.')
        # Set an existing value so the initialization branch is not taken.
        harvey.files = expected_files
        actual_files = harvey["files"]
        m_files_from_directory.assert_not_called()
        assert expected_files == actual_files


    @pytest.mark.skipif(skiptests, reason="Work in progress")
    def test_getitem_no_key_exception(self):
        """
        Test get not valid. Verify raises exception.
        """
        # Initialize Harvester instance with directory and mapfile.
        invalid_key = "sldkfjsllsdkfjlksjfd"
        harvey = Harvester('.')
        with pytest.raises(KeyError) as excinfo:
            harvey[invalid_key]
        assert excinfo.value.args[0] == "Invalid key '{}'".format(invalid_key)
