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
    @patch('photo_rename.Filemap.build_new_fn')
    def test_filemap_init_with_no_new_fn(self, m_build_new_fn):
        """
        Initialize Filemap with no dst_fn. Mock build_new_fn(). Confirm that
        dst_fn is correctly set and dst_fn_fq is fully qualified.
        """
        m_build_new_fn.return_value = "abc.jpg"
        exif_data = EXIF_DATA_VALID['exif_data']
        filemap = Filemap(os.path.join("/a/b/c/", OLD_FN_JPG_LOWER),
                IMAGE_TYPE_JPEG, metadata=exif_data)
        new_fn = "abc.jpg"
        new_fn_fq = os.path.join("/a/b/c", new_fn)
        assert filemap.new_fn == new_fn
        assert filemap.new_fn_fq == new_fn_fq

