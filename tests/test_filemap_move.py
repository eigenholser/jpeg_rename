import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from .stubs import *
from . import TEST_FILEMAP_MOVE


class TestFilemapMove(object):
    """
    Test for method move() are in this class.
    """
    skiptests = not TEST_FILEMAP_MOVE

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize("src_fn", [
        SRC_FN_JPG_LOWER, SRC_FN_JPG_UPPER])
    @patch('photo_rename.filemap.os.rename')
    @patch('photo_rename.Filemap._chmod')
    def test_move_orthodox(self, m_chmod, m_os, src_fn):
        """
        Rename file with mock os.rename. Verify called with args.
        """
        m_chmod.return_value = None
        exif_data = EXIF_DATA_NOT_VALID
        filemap = Filemap(src_fn, IMAGE_TYPE_JPEG, metadata=exif_data)
        dst_fn = filemap.dst_fn
        filemap.move()
        if src_fn == dst_fn:
            m_os.assert_not_called()
        else:
            m_os.assert_called_with(src_fn, dst_fn)

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemap.os.rename')
    @patch('photo_rename.Filemap._chmod')
    def test_move_orthodox_rename_raises_exeption(self, m_chmod, m_os):
        """
        Rename file with mocked os.rename. Verify called with args.
        """
        m_chmod.return_value = None
        m_os.side_effect = OSError((1, "Just testing.",))
        src_fn = SRC_FN_JPG_UPPER
        exif_data = EXIF_DATA_NOT_VALID
        filemap = Filemap(src_fn, IMAGE_TYPE_JPEG, metadata=exif_data)
        dst_fn = filemap.dst_fn
        filemap.move()
        m_os.assert_called_with(src_fn, dst_fn)

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemap.os.path.exists')
    @patch('photo_rename.Filemap._chmod')
    def test_move_collision_detected(self, m_chmod, m_exists):
        """
        Move file with collision_detected. Confirm collision.
        """
        m_chmod.return_value = None
        m_exists.return_value = True
        filemap = Filemap(SRC_FN_JPG_LOWER, IMAGE_TYPE_JPEG, metadata={},
                dst_fn="abc.png")
        filemap.move()
        assert filemap.collision_detected == True

