import os
import sys
import pytest
from mock import MagicMock, Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename.copy_metadata import *
from .stubs import *
from . import TEST_COPY_METADATA_MAIN


class TestCopyMetadataMain(object):
    """
    Tests for copy_metadata.py main() function.
    """
    skiptests = not TEST_COPY_METADATA_MAIN

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.copy_metadata.CustomArgumentParser')
    @patch('photo_rename.copy_metadata.process_all_files')
    @patch('photo_rename.copy_metadata.os.path.isdir')
    @patch('photo_rename.copy_metadata.os.path.exists')
    def test_copy_metadata_main_function(self,
            m_exists, m_isdir, m_process_all_files, m_argparser):
        """
        Test main() function. Mock CustomArgumentParser to return values
        desired for test. Verify process_all_files called with expected
        arguments.
        """
        m_exists.return_value = True
        m_isdir.return_value = True

        # Mock up the proper return values.
        m_parse_args = MagicMock(
                src_directory="/abc", dst_directory="/def", simon_sez=True)
        attrs = {
            'parse_args.return_value': m_parse_args,
        }

        # This one configured to return m_parse_args.
        m_parse_args_container = MagicMock()
        m_parse_args_container.configure_mock(**attrs)
        m_argparser.return_value = m_parse_args_container

        retval = main()
        m_process_all_files.assert_called_with('/abc', '/def', simon_sez=True)

