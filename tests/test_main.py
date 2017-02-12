import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from stubs import *


class TestMainFunction(object):
    """Tests for main() function."""

    class TestArgumentParser(object):
        """Stub class."""

        def add_argument(self, *args, **kwargs):
            """Stub method."""
            pass

        def parse_args(self):
            """Stub method."""

            class Args:
                """Stub class."""
                directory = '.'
                simon_sez = False
                avoid_collisions = False
                verbose = True
                mapfile = None

            return Args()

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @patch('photo_rename.argparse.ArgumentParser', TestArgumentParser)
    @patch('photo_rename.process_all_files')
    def test_main_function(self, mock_process_all_files):
        """
        Test main() function. Mock argparse and replace with stubs. Verify
        process_all_files called with expected arguments.
        """
        mock_process_all_files.return_value = 1234
        retval = main()
        mock_process_all_files.assert_called_with(workdir='.', simon_sez=False,
                avoid_collisions=False, mapfile=None)
