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
    @pytest.mark.parametrize("old_fn", [
        OLD_FN_JPG_LOWER, OLD_FN_JPG_UPPER])
    @patch('photo_rename.FileMap.make_new_fn_unique')
    @patch('photo_rename.os.rename')
    def test_move_orthodox(self, mock_os, mock_fn_unique, old_fn):
        """
        Rename file with mocked os.rename. Verify called with args.
        """
        mock_fn_unique.return_value = None
        exif_data = EXIF_DATA_NOT_VALID
        filemap = FileMap(old_fn, IMAGE_TYPE_JPEG,
                avoid_collisions=None, metadata=exif_data)
        new_fn = filemap.new_fn
        filemap.move()
        if old_fn == new_fn:
            mock_os.assert_not_called()
        else:
            mock_os.assert_called_with(old_fn, new_fn)

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.FileMap.make_new_fn_unique')
    @patch('photo_rename.os.rename')
    def test_move_orthodox_rename_raises_exeption(self, mock_os,
            mock_fn_unique):
        """
        Rename file with mocked os.rename. Verify called with args.
        """
        mock_fn_unique.return_value = None
        mock_os.side_effect = OSError((1, "Just testing.",))
        old_fn = OLD_FN_JPG_UPPER
        exif_data = EXIF_DATA_NOT_VALID
        filemap = FileMap(old_fn, IMAGE_TYPE_JPEG,
                avoid_collisions=None, metadata=exif_data)
        new_fn = filemap.new_fn
        filemap.move()
        mock_os.assert_called_with(old_fn, new_fn)

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.FileMap.make_new_fn_unique')
    @patch('photo_rename.os.rename')
    def test_move_orthodox_fn_unique_raises_exception(self, mock_os,
            mock_fn_unique):
        """
        Rename file with mocked os.rename. Verify called with args.
        """
        mock_fn_unique.side_effect = OSError((1, "Just testing.",))
        old_fn = OLD_FN_JPG_LOWER
        exif_data = EXIF_DATA_NOT_VALID
        filemap = FileMap(old_fn, IMAGE_TYPE_JPEG,
                avoid_collisions=None, metadata=exif_data)
        new_fn = filemap.new_fn
        with pytest.raises(OSError):
            filemap.move()

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.FileMap.make_new_fn_unique')
    @patch('photo_rename.os.path.exists')
    def test_move_collision_detected(self, mock_exists, mock_fn_unique):
        """Move file with collision_detected simulating avoid_collisions=False.
        """
        mock_fn_unique.return_value = None
        mock_exists.return_value = True
        old_fn = OLD_FN_JPG_LOWER
        exif_data = {}
        filemap = FileMap(old_fn, IMAGE_TYPE_JPEG,
                avoid_collisions=None, metadata=exif_data)
        filemap.collision_detected = True
        new_fn = filemap.new_fn
        filemap.move()
        assert new_fn == old_fn

