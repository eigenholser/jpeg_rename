import logging
import os
import sys
import pytest
from mock import MagicMock, Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename.set_datetime import *
from .stubs import *
from . import TEST_SET_DATETIME_PROCESS_ALL_FILES


@pytest.fixture
def initial_datetime():
    return "1999-12-31 23:59:59"

class TestSetDatetimeProcessAllFiles(object):
    """
    Tests for set_datetime.py process_all_files() function.
    """
    skiptests = not TEST_SET_DATETIME_PROCESS_ALL_FILES

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize(
        "exists, access", [
            (True, False,),
            (False, True,),
    ])
    @patch('photo_rename.set_datetime.os.path.exists')
    @patch('photo_rename.set_datetime.os.access')
    @patch('photo_rename.set_datetime.os.sys.exit')
    @patch('photo_rename.set_datetime.logger')
    def test_set_datetime_paf_with_validation_params(self, m_logger,
            m_exit, m_access, m_exists, exists, access, initial_datetime):
        """
        Test process_all_files() function. Check logic for path exists and
        access validation and handling.
        """
        m_exists.return_value = exists
        m_access.return_value = access

        # Invoke unit.
        process_all_files("/", initial_datetime, True)

        # Verify expected behavior.
        m_logger.error.assert_called_once()
        m_logger.warn.assert_called()
        m_exit.assert_called_once()

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize("simon_sez", [True, False])
    @patch('photo_rename.set_datetime.Harvester')
    @patch('photo_rename.set_datetime.FileMetadata')
    @patch('photo_rename.set_datetime.os.path.exists')
    @patch('photo_rename.set_datetime.os.access')
    @patch('photo_rename.set_datetime.os.sys.exit')
    @patch('photo_rename.set_datetime.logger')
    def test_set_datetime_paf_with_(self, m_logger, m_exit,
            m_access, m_exists, m_filemetadata, m_harvey, simon_sez,
            initial_datetime):
        """
        Test process_all_files() function. Parametrize simon_sez to test both
        cases. Mock needed properties. Verify processes two files by
        confirming method calls.
        """
        m_exists.return_value = True
        m_access.return_value = True
        interval = 1

        m_fmd_obj = MagicMock()
        fmd_attrs = {
            'set_datetime.return_value': None,
        }
        m_fmd_obj.configure_mock(**fmd_attrs)
        m_filemetadata.return_value = m_fmd_obj

        m_test = MagicMock(files=[1, 2])
        test_attrs = {
                '__getitem__.return_value': [Mock(), Mock()],
        }
        m_test.configure_mock(**test_attrs)

        m_harvey.return_value = m_test

        # Invoke unit.
        process_all_files("/", initial_datetime, interval, simon_sez)

        # Verify expected results.
        m_logger.info.assert_called()
        if simon_sez:
            m_fmd_obj.set_datetime.assert_called()
        else:
            m_fmd_obj.set_datetime.assert_not_called()

