import os
import re
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from .stubs import *
from . import TEST_FILEMAP_INIT


class TestFilemapInit(object):
    """
    Tests for Filemap constructor.
    """
    skiptests = not TEST_FILEMAP_INIT

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.Filemap.build_dst_fn')
    def test_filemap_init_with_no_dst_fn(self, m_build_dst_fn):
        """
        Initialize Filemap with no dst_fn. Mock build_dst_fn(). Confirm that
        dst_fn is correctly set and dst_fn_fq is fully qualified.
        """
        m_build_dst_fn.return_value = "abc.jpg"
        exif_data = EXIF_DATA_VALID['exif_data']
        filemap = Filemap(os.path.join("/a/b/c/", SRC_FN_JPG_LOWER),
                IMAGE_TYPE_JPEG, metadata=exif_data)
        dst_fn = "abc.jpg"
        dst_fn_fq = os.path.join("/a/b/c", dst_fn)
        assert filemap.dst_fn == dst_fn
        assert filemap.dst_fn_fq == dst_fn_fq

