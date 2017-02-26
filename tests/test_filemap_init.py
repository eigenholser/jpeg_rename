import os
import re
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from stubs import *


class TestFileMapInit():
    """
    Tests for FileMap constructor.
    """
    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @patch('photo_rename.FileMap.build_new_fn')
    def test_filemap_init_with_no_new_fn(self, mock_build_new_fn):
        """

        """
#       mock_build_new_fn.return_value = "abc.jpg"
        exif_data = EXIF_DATA_VALID['exif_data']
        filemap = FileMap(OLD_FN_JPG_LOWER, IMAGE_TYPE_JPEG,
                avoid_collisions=True, metadata=exif_data, new_fn="abc.jpg")
        new_fn = filemap.new_fn
        assert filemap.new_fn == "abc.jpg"

