import os
import re
import stat
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from .stubs import *
from . import TEST_FILEMAP_CHMOD


class StubStat(object):
    """
    Stub object for mocking out os.stat.
    """

    def __init__(self, mode):
        self.mode = mode

    @property
    def st_mode(self):
        return self.mode


class TestFilemapChmod(object):
    """
    Tests for FileMap method _chmod() are in this class.
    """
    skiptests = not TEST_FILEMAP_CHMOD

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize("st_mode", [33124, 33068, 33061])
    @patch('photo_rename.filemap.os.stat')
    @patch('photo_rename.filemap.os.chmod')
    def test_chmod_on_to_off(self, mock_chmod, mock_stat, st_mode):
        """
        Turn execute bits off one by one. Confirm that chmod called once.

        st_mode=33124 '0b1000000101100100'
        st_mode=33068 '0b1000000100101100'
        st_mode=33061 '0b1000000100100101'
        """
        mock_stat.return_value = StubStat(st_mode)
        old_fn = OLD_FN_JPG_LOWER
        exif_data = EXIF_DATA_NOT_VALID
        filemap = FileMap(old_fn, IMAGE_TYPE_JPEG, metadata=exif_data)
        filemap._chmod()
        assert mock_chmod.assert_called_once

