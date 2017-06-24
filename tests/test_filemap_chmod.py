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
    Tests for Filemap method _chmod() are in this class.
    """
    skiptests = not TEST_FILEMAP_CHMOD

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize(
        "st_mode_supplied, st_mode_expected", [
            (33124, 0b1000000100100100),
            (33068, 0b1000000100100100),
            (33061, 0b1000000100100100),
            (33279, 0b1000000110110110),])
    @patch('photo_rename.filemap.os.stat')
    @patch('photo_rename.filemap.os.chmod')
    def test_chmod_on_to_off(self, mock_chmod, mock_stat, st_mode_supplied,
            st_mode_expected):
        """
        Turn execute bits off one by one. Confirm that chmod called once.

        st_mode=33124 '0b1000000101100100'
        st_mode=33068 '0b1000000100101100'
        st_mode=33061 '0b1000000100100101'
        st_mode=33279 '0b1000000111111111'
        """
        # This maps the supplied st_mode to the expected st_mode after chmod.
        mock_stat.return_value = StubStat(st_mode_supplied)
        src_fn = SRC_FN_JPG_LOWER
        exif_data = EXIF_DATA_NOT_VALID
        filemap = Filemap(src_fn, IMAGE_TYPE_JPEG, metadata=exif_data)
        filemap._chmod()
        # These three update only one bit each, called once each st_mode.
        if st_mode_supplied in [33124, 33068, 33061]:
            mock_chmod.assert_called_once_with(src_fn, st_mode_expected)
        # This one updates 3 bits and makes three chmod calls. Mock seems to
        # recognize only the final. Check that one.
        if st_mode_supplied == 33279:
            mock_chmod.assert_called_with(src_fn, st_mode_expected)

