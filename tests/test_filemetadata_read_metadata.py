from datetime import datetime
import os
import re
import sys
import pytest
from mock import call, MagicMock, Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from .stubs import *
from . import (
        TEST_FILEMETADATA_READ_METADATA, TEST_FILEMETADATA_SET_DATETIME,
        TEST_FILEMETADATA_COPY_METADATA, TEST_FILEMETADATA_GETITEM)


@pytest.fixture
def exception():
    """
    Fixture for raising exception.
    """
    return Exception("Surprise!")


@pytest.fixture
def expected_metadata():
    """
    Metadata for reuse.
    """
    return {"abc": 123}


class TestFileMetadataReadMetadata(object):
    """
    Tests for FileMetadata method read_metadata() are in this class.
    """
    skiptests = not TEST_FILEMETADATA_READ_METADATA

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemetadata.pyexiv2.ImageMetadata')
    def test_filemetadata_read_metadata(self, m_img_md):
        """
        Test read_metadata() method with mocked pyexiv2.ImageMetadata object.
        Mock keys expected and __getitem__ to return some value. Confirm
        expected value is returned.
        """
        exif_keys = ['Exif.Image.DateTime']
        xmp_keys = ['Xmp.xmp.CreateDate']
        attrs = {
            # Return exif_keys
            'exif_keys': exif_keys,
            # Return xmp_keys
            'xmp_keys': xmp_keys,
            # Return 1 for everything?
            '__getitem__.return_value': Mock(raw_value=1),
        }
        # Create a mock that will return meaningful values for testing the
        # unit.
        m_keys = MagicMock()
        m_keys.configure_mock(**attrs)

        # Return the mock when pyexiv2.ImageMetadata(src_fn) is called.
        m_img_md.return_value = m_keys

        # Instantiate with any filename. Mock prevents read.
        filemd = FileMetadata("file.jpg")

        expected_metadata = {exif_keys[0]: 1, xmp_keys[0]: 1}
        assert filemd.read_metadata() == expected_metadata


class TestFileMetadataSetDatetime(object):
    """
    Tests for FileMetadata method set_datetime() are in this class.
    """
    skiptests = not TEST_FILEMETADATA_SET_DATETIME

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize(
        "metadata", [
            {'Exif.Image.DateTime': 1},
            {'Xmp.xmp.CreateDate': 1},
            {'Exif.Photo.DateTimeOriginal': 1},
        ])
    @patch('photo_rename.filemetadata.pyexiv2.ImageMetadata')
    @patch('photo_rename.filemetadata.pyexiv2.ExifTag')
    @patch('photo_rename.filemetadata.pyexiv2.XmpTag')
    def test_filemetadata_set_datetime_all_tags(self,
            m_xmp_tag, m_exif_tag, m_img_md, metadata):
        """
        Test set_datetime() with parametrized metadata. Exercises all
        branches. Confirm methods called with proper arguments under specific
        conditions.
        """

        new_datetime = datetime.now()
        filemd = FileMetadata("file.png")
        filemd.metadata = metadata
        filemd.set_datetime(new_datetime)
        if metadata.get('Exif.Photo.DateTimeOriginal'):
            call1 = call('Exif.Photo.DateTimeOriginal', new_datetime)
            call2 = call('Exif.Image.DateTime', new_datetime)
            m_exif_tag.assert_has_calls([call1, call2])
            m_xmp_tag.assert_not_called()
        if metadata.get('Xmp.xmp.CreateDate'):
            m_exif_tag.assert_called_with('Exif.Image.DateTime', new_datetime)
            m_xmp_tag.assert_called_with('Xmp.xmp.CreateDate', new_datetime)
        filemd.img_md.write.assert_called_once()

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemetadata.logger')
    @patch('photo_rename.filemetadata.pyexiv2.ImageMetadata')
    @patch('photo_rename.filemetadata.pyexiv2.ExifTag')
    @patch('photo_rename.filemetadata.pyexiv2.XmpTag')
    def test_filemetadata_set_datetime_exception(self,
            m_xmp_tag, m_exif_tag, m_img_md, m_logger, exception):
        """
        Test set_datetime() method with Exception raised on write() call.
        Verify exception handled by mocking logger and confirm
        called_once_with(exception). Also, just to be pedantic, verify
        img_md.write() called once.
        """
        new_datetime = datetime.now()
        # Raise this exception when write() called.
        md_attrs = {
            'write.side_effect': exception,
            '__getitem__.return_value': Mock(raw_value=1),
        }
        m_write = MagicMock()
        m_write.configure_mock(**md_attrs)
        m_img_md.return_value = m_write
        filemd = FileMetadata("file.jpg")
        filemd.metadata = {"One fish": "Two Fish"}
        # Will fall through and call filemd.img_md.write()...boom!
        filemd.set_datetime(new_datetime)
        # Confirm img_md.write() called.
        filemd.img_md.write.assert_called_once()
        # Confirm exception raised by proxy.
        m_logger.error.assert_called_once_with(exception)


class TestFileMetadataCopyMetadata(object):
    """
    Tests for FileMetadata method copy_metadata() are in this class.
    """
    skiptests = not TEST_FILEMETADATA_COPY_METADATA

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize("mime_type", ["image/png", "image/tiff"])
    @patch('photo_rename.filemetadata.pyexiv2.ImageMetadata')
    def test_filemetadata_copy_metadata_mime_types(self, m_img_md, mime_type):
        """
        Test copy_metadata() method with two parametrized mime types that
        cover each branch of the conditional. Verify the ImageMetadata.copy()
        method call for each case.
        """
        imd = MagicMock(mime_type=mime_type)
        m_img_md.return_value = imd
        filemd = FileMetadata("file.tiff")
        filemd.copy_metadata("other.tiff")

        # Call varies by mime_type.
        if mime_type == "image/tiff":
            comment = False
        else:
            comment = True

        # Assert correct call to confirm test.
        filemd.img_md.copy.assert_called_once_with(filemd.img_md,
                exif=True, iptc=True, xmp=True, comment=comment)

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemetadata.logger')
    @patch('photo_rename.filemetadata.pyexiv2.ImageMetadata')
    def test_filemetadata_copy_metadata_exception(self,
            m_img_md, m_logger, exception):
        """
        Test copy_metadata() method with exception. Verify
        ImageMetadata.write() called. Verify logger.error(exception) called
        which confirms exception handling.
        """
        # Raise this exception when write() called.
        attrs = {'write.side_effect': exception,}
        m_write = MagicMock()
        m_write.configure_mock(**attrs)
        m_img_md.return_value = m_write
        filemd = FileMetadata("file.tiff")
        # Will fall through and call filemd.img_md.write()...boom!
        filemd.copy_metadata("other.tiff")
        # Confirm img_md.write() called.
        filemd.img_md.write.assert_called_once()
        # Confirm exception raised by proxy.
        m_logger.error.assert_called_once_with(exception)


class TestFileMetadataGetitem(object):
    """
    Tests for FileMetadata magic method __getitem__().
    """
    skiptests = not TEST_FILEMETADATA_GETITEM

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.FileMetadata.read_metadata')
    @patch('photo_rename.filemetadata.pyexiv2.ImageMetadata')
    def test_filemetadata_getitem_not_initialized(self,
            m_img_md, m_read_metadata, expected_metadata):
        """
        Test __getitem__() with metadata not yet initialized. Mocked
        read_metadata() method call expected to be called. Confirm called
        once. Also verify expected versus actual.
        """
        m_read_metadata.return_value = expected_metadata
        filemd = FileMetadata("file.png")
        actual_metadata = filemd["metadata"]
        m_read_metadata.assert_called_once()
        assert actual_metadata == expected_metadata

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemetadata.pyexiv2.ImageMetadata')
    def test_filemetadata_getitem_initialized(self,
            m_img_md, expected_metadata):
        """
        Test __getitem__() with metadata already initialized. Expect metadata
        to be returned from object property.
        """
        filemd = FileMetadata("file.png")
        filemd.metadata = expected_metadata
        actual_metadata = filemd["metadata"]
        assert actual_metadata == expected_metadata

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.filemetadata.pyexiv2.ImageMetadata')
    def test_filemetadata_getitem_keyerror(self, m_img_md):
        """
        """
        invalid_key = "slkdfj"
        filemd = FileMetadata("file.xyz")
        with pytest.raises(KeyError) as excinfo:
            filemd[invalid_key]
        assert excinfo.value.args[0] == "Invalid key '{}'".format(invalid_key)
