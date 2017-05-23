import os
import sys
import pytest
from mock import MagicMock, Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename.set_datetime import *
from .stubs import *
from . import TEST_SET_DATETIME_MAIN


class TestCopyMetadataMain(object):
    """
    Tests for copy_metadata.py main() function.
    """
    skiptests = not TEST_SET_DATETIME_MAIN

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.set_datetime.CustomArgumentParser')
    @patch('photo_rename.set_datetime.process_all_files')
    @patch('photo_rename.set_datetime.os.path.isdir')
    @patch('photo_rename.set_datetime.os.path.exists')
    def test_set_datetime_main_args_happy_path(self,
            m_exists, m_isdir, m_process_all_files, m_argparser):
        """
        Test main() function. Mock CustomArgumentParser to return values
        desired for test. Verify process_all_files called with expected
        arguments.
        """
        workdir = "/abc"
        new_datetime = "1999-12-31 23:59:59"
        interval = "1"
        m_exists.return_value = True
        m_isdir.return_value = True

        # Mock up the proper return values.
        m_parse_args = MagicMock(directory=workdir, datetime=new_datetime,
                interval=interval, simon_sez=True)
        attrs = {
            'parse_args.return_value': m_parse_args,
        }

        # This one configured to return m_parse_args.
        m_parse_args_container = MagicMock()
        m_parse_args_container.configure_mock(**attrs)
        m_argparser.return_value = m_parse_args_container

        retval = main()
        m_process_all_files.assert_called_with(
                workdir, new_datetime, int(interval), simon_sez=True)

