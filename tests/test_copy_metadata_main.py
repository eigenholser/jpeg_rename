import logging
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
    @pytest.mark.parametrize(
        "verbose, log_level", [
            (False, logging.INFO,),
            (True, logging.DEBUG,),
    ])
    @patch('photo_rename.copy_metadata.CustomArgumentParser')
    @patch('photo_rename.copy_metadata.process_all_files')
    @patch('photo_rename.copy_metadata.os.path.isdir')
    @patch('photo_rename.copy_metadata.os.path.exists')
    @patch('photo_rename.copy_metadata.logging')
    def test_copy_metadata_main_args_with_verbose_params(self,
            m_logging, m_exists, m_isdir, m_process_all_files, m_argparser,
            verbose, log_level):
        """
        Test main() function. Mock CustomArgumentParser to return values
        desired for test. Parametrize different combinations of verbosity
        and log level. Verify that logging configured properly for verbose
        setting.
        """
        m_exists.return_value = True
        m_isdir.return_value = True

        # Mock up the proper return values.
        m_parse_args = MagicMock(
            src_directory="/abc",
            dst_directory="/def",
            simon_sez=True,
            verbose=verbose,
        )

        attrs = {
            'parse_args.return_value': m_parse_args,
        }

        # This one configured to return m_parse_args.
        m_parse_args_container = MagicMock()
        m_parse_args_container.configure_mock(**attrs)
        m_argparser.return_value = m_parse_args_container

        # Invoke the unit.
        retval = main()

        # Confirm expected behavior
        m_logging.basicConfig.called_once_with(level=log_level)
        m_process_all_files.assert_called_with('/abc', '/def', simon_sez=True)


    # TODO: Check the m_exit mock. Is it useful? Something wrong with this.
    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.copy_metadata.CustomArgumentParser')
    @patch('photo_rename.copy_metadata.process_all_files')
    @patch('photo_rename.copy_metadata.os.path.isdir')
    @patch('photo_rename.copy_metadata.os.path.exists')
    @patch('photo_rename.copy_metadata.os.sys.exit')
    @patch('photo_rename.copy_metadata.logger')
    def test_copy_metadata_main_missing_directory(self, m_logger, m_exit,
            m_exists, m_isdir, m_process_all_files, m_argparser):
        """
        Test main() function. Mock CustomArgumentParser to return values
        desired for test but with missing `src_directory`. Verify correct
        behavior by asserting calls on logger, usage_message, and exit.
        """
        m_exists.return_value = True
        m_isdir.return_value = True

        # Mock up the proper return values.
        m_parse_args = MagicMock(
            src_directory=None,
            dst_directory="/def",
            simon_sez=True,
            verbose=False,
        )

        attrs = {
            'parse_args.return_value': m_parse_args,
            'usage_message.return_value': None,
        }

        # This one configured to return m_parse_args.
        m_parse_args_container = MagicMock()
        m_parse_args_container.configure_mock(**attrs)
        m_argparser.return_value = m_parse_args_container

        # Invoke the unit.
        retval = main()

        # Confirm expected behavior
        m_logger.error.assert_called()
        m_parse_args_container.usage_message.assert_called_once()
        m_exit.assert_called_once_with(1)

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.copy_metadata.CustomArgumentParser')
    @patch('photo_rename.copy_metadata.process_all_files')
    @patch('photo_rename.copy_metadata.os.path.isdir')
    @patch('photo_rename.copy_metadata.os.path.exists')
    @patch('photo_rename.copy_metadata.os.sys.exit')
    def test_copy_metadata_main_path_not_exist(self, m_exit, m_exists,
            m_isdir, m_process_all_files, m_argparser):
        """
        Test main() function. Mock CustomArgumentParser to return values
        desired for test. Mock os.path.exists to return False. Verify
        usage_message() called once.
        """
        m_exists.return_value = False
        m_isdir.return_value = True

        # Mock up the proper return values.
        m_parse_args = MagicMock(
            src_directory="/abc",
            dst_directory="/def",
            simon_sez=True,
            verbose=False,
        )

        attrs = {
            'parse_args.return_value': m_parse_args,
            'usage_message.return_value': None,
        }

        # This one configured to return m_parse_args.
        m_parse_args_container = MagicMock()
        m_parse_args_container.configure_mock(**attrs)
        m_argparser.return_value = m_parse_args_container

        # Invoke the unit.
        retval = main()

        # Confirm expected behavior
        m_exit.assert_called_once_with(1)
        m_parse_args_container.usage_message.assert_called_once()

