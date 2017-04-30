import os
import re
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import Filemap
from photo_rename import *
from .stubs import *
from . import TEST_FILEMAP_BUILD_DST_FN


class TestFilemapBuildNewFn(object):
    """
    Tests for method build_dst_fn() are in this class.
    """
    skiptests = not TEST_FILEMAP_BUILD_DST_FN

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize(
        "src_fn, image_type, expected_dst_fn, exif_data", [
        (SRC_FN_JPG_LOWER, IMAGE_TYPE_JPEG,
            EXIF_DATA_VALID['expected_dst_fn'],
            EXIF_DATA_VALID['exif_data'],),
        (SRC_FN_JPG_LOWER, IMAGE_TYPE_JPEG, SRC_FN_JPG_LOWER,
            EXIF_DATA_NOT_VALID),
        (SRC_FN_JPG_LOWER, IMAGE_TYPE_JPEG, SRC_FN_JPG_LOWER, {},),
        (SRC_FN_JPEG, IMAGE_TYPE_JPEG, SRC_FN_JPG_LOWER, {},),
        (SRC_FN_JPEG, IMAGE_TYPE_PNG, SRC_FN_JPG_LOWER, {},),
    ])
    def test_build_dst_fn_parametrized_exif_data(
            self, src_fn, image_type, expected_dst_fn, exif_data):
        """
        Test build_dst_fn() with various EXIF data.
        """
        filemap = Filemap(src_fn, image_type, exif_data)
        dst_fn = filemap.dst_fn
        assert dst_fn == expected_dst_fn
