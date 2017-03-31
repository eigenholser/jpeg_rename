import os
import re
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from .stubs import *
from . import TEST_FILEMAP_RENAME


class TestFilemapRename(object):
    """
    Tests for method build_new_fn() are in this class.
    """
    skiptests = not TEST_FILEMAP_RENAME

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemap.os.path.exists')
    def test_rename_empty_exif_data(self, mock_exists):
        """
        Make unique filename with empty EXIF data.
        """
        mock_exists.return_value = True
        old_fn = OLD_FN_JPG_LOWER
        exif_data = EXIF_DATA_NOT_VALID
        filemap = FileMap(old_fn, IMAGE_TYPE_JPEG,
                avoid_collisions=True, metadata=exif_data)
        new_fn = filemap.new_fn
        filemap.make_new_fn_unique()
        assert filemap.new_fn == old_fn

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemap.os.path.exists')
    def test_rename_with_valid_exif_data_and_avoid_collisions(self,
            mock_exists):
        """
        Make unique new filename from valid EXIF data. Avoid collisions.
        """
        mock_exists.return_value = True
        exif_data = EXIF_DATA_VALID['exif_data']
        filemap = FileMap(OLD_FN_JPG_LOWER, IMAGE_TYPE_JPEG,
                avoid_collisions=True, metadata=exif_data)
        counter = 2
        new_fn = filemap.new_fn
        renamed_fn = re.sub(
                r"^(\d+_\d+)\.jpg", r"\1-{}.jpg".format(counter), new_fn)
        filemap.MAX_RENAME_ATTEMPTS = counter
        with pytest.raises(Exception):
            filemap.make_new_fn_unique()
        assert filemap.new_fn == renamed_fn

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemap.os.path.exists')
    def test_rename_with_valid_exif_data_and_no_avoid_collisions(self,
            mock_exists):
        """
        Make unique new filename from valid EXIF data. Do not avoid
        collisions.
        """
        mock_exists.return_value = True
        old_fn = OLD_FN_JPG_LOWER
        exif_data = EXIF_DATA_VALID['exif_data']
        filemap = FileMap(old_fn, IMAGE_TYPE_JPEG,
                avoid_collisions=False, metadata=exif_data)
        new_fn = filemap.new_fn
        filemap.MAX_RENAME_ATTEMPTS = 2
        filemap.make_new_fn_unique()
        assert filemap.new_fn == EXIF_DATA_VALID['expected_new_fn']

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemap.os.path.exists')
    def test_rename_no_collision(self, mock_exists):
        """
        Make unique new filename from valid EXIF data. Do not avoid
        collisions.
        """
        mock_exists.return_value = False
        old_fn = OLD_FN_JPG_LOWER
        exif_data = {}
        filemap = FileMap(old_fn, IMAGE_TYPE_JPEG,
                avoid_collisions=False, metadata=exif_data)
        new_fn = filemap.new_fn
        filemap.make_new_fn_unique()
        assert filemap.new_fn == old_fn
