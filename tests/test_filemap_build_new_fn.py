import os
import re
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from stubs import *


class TestBuildNewFn():
    """
    Tests for method build_new_fn() are in this class.
    """
    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @pytest.mark.parametrize(
        "old_fn, image_type, expected_new_fn, exif_data", [
        (OLD_FN_JPG_LOWER, IMAGE_TYPE_JPEG,
            EXIF_DATA_VALID['expected_new_fn'],
            EXIF_DATA_VALID['exif_data'],),
        (OLD_FN_JPG_LOWER, IMAGE_TYPE_JPEG, OLD_FN_JPG_LOWER,
            EXIF_DATA_NOT_VALID),
        (OLD_FN_JPG_LOWER, IMAGE_TYPE_JPEG, OLD_FN_JPG_LOWER, {},),
        (OLD_FN_JPEG, IMAGE_TYPE_JPEG, OLD_FN_JPG_LOWER, {},),
        (OLD_FN_JPEG, IMAGE_TYPE_PNG, OLD_FN_JPG_LOWER, {},),
    ])
    def test_build_new_fn_parametrized_exif_data(
            self, old_fn, image_type, expected_new_fn, exif_data):
        """
        Test build_new_fn() with various EXIF data.
        """
        filemap = FileMap(old_fn, image_type, None, exif_data)
        new_fn = filemap.new_fn
        assert new_fn == expected_new_fn
