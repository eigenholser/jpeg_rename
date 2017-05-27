import os
import sys
import pytest
from mock import MagicMock, Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename.set_datetime import *
from .stubs import *
from . import TEST_SET_DATETIME_MAIN


@pytest.fixture
def new_datetime():
    return "1999-12-31 23:59:59"

class TestSetDatetimeMain(object):
    """
    Tests for set_datetime.py main() function.
    """
    skiptests = not TEST_SET_DATETIME_MAIN

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize(
        "verbose, log_level", [
            (False, logging.INFO,),
            (True, logging.DEBUG,),
    ])
    @patch('photo_rename.set_datetime.CustomArgumentParser')
    @patch('photo_rename.set_datetime.process_all_files')
    @patch('photo_rename.set_datetime.os.path.isdir')
    @patch('photo_rename.set_datetime.os.path.exists')
    @patch('photo_rename.set_datetime.logging')
    def test_set_datetime_main_args_with_verbose_params(self,
            m_logging, m_exists, m_isdir, m_process_all_files, m_argparser,
            verbose, log_level, new_datetime):
        """
        Test main() function. Mock CustomArgumentParser to return values
        desired for test. Verify process_all_files called with expected
        arguments.
        """
        workdir = "/abc"
        interval = "1"
        m_exists.return_value = True
        m_isdir.return_value = True

        # Mock up the proper return values.
        m_parse_args = MagicMock(
            directory=workdir,
            datetime=new_datetime,
            interval=interval,
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

        # Invovke the unit.
        retval = main()

        # Confirm expected behavior.
        m_logging.basicConfig.called_once_with(level=log_level)
        m_process_all_files.assert_called_with(
                workdir, new_datetime, int(interval), simon_sez=True)

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize("workdir", ["/abc/def", None])
    @patch('photo_rename.set_datetime.CustomArgumentParser')
    @patch('photo_rename.set_datetime.process_all_files')
    @patch('photo_rename.set_datetime.os.path.isdir')
    @patch('photo_rename.set_datetime.os.path.exists')
    def test_set_datetime_main_args_with_workdir_params(self,
            m_exists, m_isdir, m_process_all_files, m_argparser,
            workdir, new_datetime):
        """
        Test set_datetime main() function. Paramatrize workdir. Mock all
        necessary arguments. Confirm process_all_files() method call is
        correct.
        """
        interval = "1"
        m_exists.return_value = True
        m_isdir.return_value = True

        # Mock up the proper return values.
        m_parse_args = MagicMock(
            directory=workdir,
            datetime=new_datetime,
            interval=interval,
            simon_sez=True,
        )

        attrs = {
            'parse_args.return_value': m_parse_args,
        }

        # This one configured to return m_parse_args.
        m_parse_args_container = MagicMock()
        m_parse_args_container.configure_mock(**attrs)
        m_argparser.return_value = m_parse_args_container

        # Invovke the unit.
        retval = main()

        expected_workdir = workdir
        if workdir is None:
            expected_workdir = os.getcwd()

        # Confirm expected behavior.
        m_process_all_files.assert_called_with(
                expected_workdir, new_datetime, int(interval), simon_sez=True)

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.set_datetime.CustomArgumentParser')
    @patch('photo_rename.set_datetime.process_all_files')
    @patch('photo_rename.set_datetime.os.path.isdir')
    @patch('photo_rename.set_datetime.os.path.exists')
    @patch('photo_rename.set_datetime.re.match')
    @patch('photo_rename.set_datetime.os.sys.exit')
    @patch('photo_rename.set_datetime.logger')
    def test_set_datetime_main_args_invalid_datetime(self, m_logger,
            m_exit, m_match, m_exists, m_isdir, m_process_all_files,
            m_argparser, new_datetime):
        """
        Test set_datetime main() function. Mock re.match() and set return
        value = False for datetime validity check. Verify correct behavior
        by confirming correct calls to logger, usage_message, and exit.
        """
        workdir = "/abc/def"
        interval = "1"
        m_exists.return_value = True
        m_isdir.return_value = True
        m_match.return_value = False

        # Mock up the proper return values.
        m_parse_args = MagicMock(
            directory=workdir,
            datetime=new_datetime,
            interval=interval,
            simon_sez=True,
        )

        attrs = {
            'parse_args.return_value': m_parse_args,
            'usage_message.return_value': None,
        }

        # This one configured to return m_parse_args.
        m_parse_args_container = MagicMock()
        m_parse_args_container.configure_mock(**attrs)
        m_argparser.return_value = m_parse_args_container

        # Invovke the unit.
        retval = main()

        # Confirm expected behavior.
        m_logger.error.assert_called()
        m_parse_args_container.usage_message.assert_called_once()
        m_exit.assert_called_once()

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize("interval", ["60", None])
    @patch('photo_rename.set_datetime.CustomArgumentParser')
    @patch('photo_rename.set_datetime.process_all_files')
    @patch('photo_rename.set_datetime.os.path.isdir')
    @patch('photo_rename.set_datetime.os.path.exists')
    @patch('photo_rename.set_datetime.logger')
    def test_set_datetime_main_args_with_interval_params(self, m_logger,
            m_exists, m_isdir, m_process_all_files, m_argparser, interval,
            new_datetime):
        """
        Test set_datetime main() function. Parametrize interval. Mock needed
        args. Verify correct behavior by confirming method calls.
        """
        workdir = "/"
        m_exists.return_value = True
        m_isdir.return_value = True

        # Mock up the proper return values.
        m_parse_args = MagicMock(
            directory=workdir,
            datetime=new_datetime,
            interval=interval,
            simon_sez=True,
        )

        attrs = {
            'parse_args.return_value': m_parse_args,
            'usage_message.return_value': None,
        }

        # This one configured to return m_parse_args.
        m_parse_args_container = MagicMock()
        m_parse_args_container.configure_mock(**attrs)
        m_argparser.return_value = m_parse_args_container

        # Invovke the unit.
        retval = main()

        expected_interval = interval
        if interval is None:
            expected_interval = "1"

        # Confirm expected behavior.
        if interval is None:
            m_logger.warn.assert_called_once()
        m_process_all_files.assert_called_with(
                workdir, new_datetime, int(expected_interval), simon_sez=True)

