import logging
import os
import sys
import pytest
from mock import MagicMock, Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename.copy_metadata import *
from .stubs import *
from . import TEST_COPY_METADATA_PROCESS_ALL_FILES


class TestCopyMetadataProcessAllFiles(object):
    """
    Tests for copy_metadata.py process_all_files() function.
    """
    skiptests = not TEST_COPY_METADATA_PROCESS_ALL_FILES

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.copy_metadata.Harvester')
    @patch('photo_rename.copy_metadata.os.path.exists')
    @patch('photo_rename.copy_metadata.os.access')
    @patch('photo_rename.copy_metadata.logger')
    def test_copy_metadata_paf_no_files(self,
            m_logger, m_access, m_exists, m_harvey):
        """
        Test process_all_files() function. No files available. Verify
        logger.warn() called once.
        """
        src_directory = "/"
        dst_directory = "/"
        simon_sez = True

        m_exists.return_value = True
        m_access.return_value = True

        # Invoke the unit.
        process_all_files(src_directory, dst_directory, simon_sez)

        # Confirm expected behavior.
        m_logger.warn.assert_called_once()

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize("simon_sez", [True, False])
    @patch('photo_rename.copy_metadata.Harvester')
    @patch('photo_rename.copy_metadata.FileMetadata')
    @patch('photo_rename.copy_metadata.os.path.exists')
    @patch('photo_rename.copy_metadata.os.access')
    @patch('photo_rename.copy_metadata.logger')
    def test_copy_metadata_paf_with_files(self, m_logger, m_access, m_exists,
            m_filemetadata, m_harvey, simon_sez):
        """
        Test process_all_files() function. Files are available. Mock up all
        the moving parts. Verify copy_metadata() called. Verify logger.warn()
        not called.
        """
        src_directory = "/"
        dst_directory = "/"

        m_exists.return_value = True
        m_access.return_value = True

        # Create a test mock that we can use for call verification.
        m_fmd_obj = MagicMock()
        fmd_attrs = {
            'copy_metadata.return_value': None,
        }
        m_fmd_obj.configure_mock(**fmd_attrs)
        m_filemetadata.return_value = m_fmd_obj

        # Create test mock that will return values for filemaps.get()
        m_filemaplist = MagicMock()
        fml_attrs = {'get.return_value': [Mock(), Mock()]}
        m_filemaplist.configure_mock(**fml_attrs)

        # Create test mock that returns some values for harvey["filemaps"]
        m_test = MagicMock(filemaps=[1, 2])
        test_attrs = {
            '__getitem__.return_value': m_filemaplist,
        }
        m_test.configure_mock(**test_attrs)

        # Harvester can just return the test mock.
        m_harvey.return_value = m_test

        # Invoke the unit.
        process_all_files(src_directory, dst_directory, simon_sez)

        # Confirm expected behavior.
        m_logger.info.assert_called()
        if simon_sez:
            m_fmd_obj.copy_metadata.assert_called()
        m_logger.warn.assert_not_called()

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize(
        "exists, access", [
            (True, False,),
            (False, True,),
    ])
    @patch('photo_rename.copy_metadata.os.path.exists')
    @patch('photo_rename.copy_metadata.os.access')
    @patch('photo_rename.copy_metadata.os.sys.exit')
    @patch('photo_rename.copy_metadata.logger')
    def test_copy_metadata_paf_with_validation_params(self, m_logger,
            m_exit, m_access, m_exists, exists, access):
        """
        Test process_all_files() function. Check logic for path exists and
        access validation and handling.
        """
        m_exists.return_value = exists
        m_access.return_value = access

        process_all_files("/", "/", True)
        m_logger.error.assert_called_once()
        m_logger.warn.assert_called()
        m_exit.assert_called_once()

