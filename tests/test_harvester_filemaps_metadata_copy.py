import os
import sys
import pytest
from mock import MagicMock, Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

import photo_rename
from photo_rename.rename import *
from .stubs import *
from . import (TEST_HARVESTER_FILEMAPS_FOR_METADATA_COPY)


class TestFilemapsForMetadataCopy():
    """
    Tests for function filemaps_for_metadata_copy() are in this class.
    """
    skiptests = not TEST_HARVESTER_FILEMAPS_FOR_METADATA_COPY

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.FilemapList')
    @patch('photo_rename.harvester.Filemap')
    @patch('photo_rename.harvester.os.listdir')
    def test_filemaps_for_metadata_copy_one_match(
            self, m_listdir, m_filemap, m_filemaplist):
        """
        Test filemaps_for_metadata_copy(). One file with matching prefix.
        Confirm that filemaps.add() called once.
        """
        src_files = ['12.tiff', '34.tiff']
        dst_files = ['12.jpg', '45.jpg']
        m_listdir.return_value = dst_files
        harvey = Harvester('/src/dir', metadata_dst_directory="/dst/dir")
        harvey.files = src_files
        actual_filemaps = harvey.filemaps_for_metadata_copy()
        actual_filemaps.add.assert_called_once()

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.FilemapList')
    @patch('photo_rename.harvester.Filemap')
    @patch('photo_rename.harvester.os.listdir')
    def test_filemaps_for_metadata_copy_no_match(
            self, m_listdir, m_filemap, m_filemaplist):
        """
        Test filemaps_for_metadata_copy(). No files with matching prefix.
        Confirm that filemaps.add() not called.
        """
        src_files = ['12.tiff', '34.tiff']
        dst_files = ['0.jpg', '45.jpg']
        m_listdir.return_value = dst_files
        harvey = Harvester('/src/dir', metadata_dst_directory="/dst/dir")
        harvey.files = src_files
        actual_filemaps = harvey.filemaps_for_metadata_copy()
        actual_filemaps.add.assert_not_called()

