import os
import re
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from .stubs import *
from . import TEST_FILEMAP_READ_METADATA, TEST_FILEMAP_READ_EXIFDATA


class StubTag(object):

    @property
    def raw_value(self):
        return EXIF_DATA_VALID["exif_data"]["Exif.Image.DateTime"]

class StubImageMetadata(object):

    def __getitem__(self, key):
        return StubTag()

    def read(self):
        return None

    @property
    def exif_keys(self):
        return EXIF_DATA_VALID["exif_data"].keys()

    @property
    def xmp_keys(self):
        return EXIF_DATA_VALID["exif_data"].keys()


class TestFilemapReadMetadata(object):
    """
    Tests for FileMap method read_metadata() are in this class.
    """
    skiptests = not TEST_FILEMAP_READ_METADATA

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemap.pyexiv2.ImageMetadata')
    def test_read_metadata(self, mock_pyexiv2):
        """
        Mock with valid metadata. Confirm metadata returned as expected.
        """
        metadata = {'Exif.Image.DateTime': '2014:08:26 06:20:20'}
        mock_pyexiv2.return_value = StubImageMetadata()
        old_fn = OLD_FN_JPG_LOWER
        exif_data = EXIF_DATA_NOT_VALID
        filemap = FileMap(old_fn, IMAGE_TYPE_PNG, avoid_collisions=True,
                new_fn="abc.jpg")
        assert filemap.read_metadata() == metadata


class TestFilemapReadExifData(object):
    """Tests for method read_exif_data() are in this class."""
    skiptests = not TEST_FILEMAP_READ_EXIFDATA

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemap.pyexiv2.ImageMetadata')
    def test_read_exif_data(self, mock_img_md):
        """Tests read_exif_data() with valid EXIF data. Tests for normal
        operation. Verify expected EXIF data in instantiated object."""

        class StubExifTag(object):
            raw_value = EXIF_DATA_VALID['exif_data']['Exif.Image.DateTime']

        class TestImage(object):
            """
            ImageMetadata test stub.
            """
            def __getitem__(self, key):
                return StubExifTag()

            def read(self):
                return EXIF_DATA_VALID['exif_data']

            @property
            def exif_keys(self):
                return ['Exif.Image.DateTime']


        old_fn = OLD_FN_JPG_LOWER
        mock_img_md.return_value = TestImage()
        filemap = FileMap(old_fn, IMAGE_TYPE_JPEG)
        assert filemap.metadata == EXIF_DATA_VALID['exif_data']

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemap.pyexiv2.ImageMetadata')
    def test_read_exif_data_info_none(self, mock_img_md):
        """
        Tests read_exif_data() with no EXIF data available. Tests for raised
        Exception. Verify expected exception message.
        """

        class TestImage(object):
            """
            ImageMetadata test stub.
            """
            def read(self):
                return None

            @property
            def exif_keys(self):
                return []

        old_fn = OLD_FN_JPG_LOWER
        mock_img_md.return_value = TestImage()
        with pytest.raises(Exception) as excinfo:
            filemap = FileMap(old_fn, IMAGE_TYPE_JPEG)
        assert str(excinfo.value) == "{0} has no EXIF data.".format(old_fn)

