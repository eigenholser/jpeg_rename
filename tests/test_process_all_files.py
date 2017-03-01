import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from stubs import *


class TestProcessAllFiles():
    """Tests for the function process_all_files() are in this class."""
    @pytest.mark.skipif(True, reason="Obsolete. Code moved to main(). Relocate test.")
    @patch('photo_rename.init_file_map')
    @patch('photo_rename.os.access')
    @patch('photo_rename.os.path.dirname')
    @patch('photo_rename.os.path.exists')
    @patch('photo_rename.os.path.abspath')
    def test_process_all_files_workdir_none(self, mock_abspath, mock_exists,
            mock_dirname, mock_os_access, mock_init_file_map):
        """
        Test process_all_files() with workdir=None, avoid_collisions=None.
        Verify that init_file_map() is called with (DIRNAME, None).
        """
        DIRNAME = '/foo/bar'
        mock_abspath.return_value = DIRNAME
        mock_exists.return_value = True
        mock_dirname.return_value = DIRNAME
        process_all_files()
        mock_init_file_map.assert_called_with(DIRNAME, None)

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @patch('photo_rename.process_file_map')
    @patch('photo_rename.init_file_map')
    @patch('photo_rename.os.access')
    def test_process_all_files_workdir_not_none(self, mock_os_access,
            mock_init_file_map, mock_process_file_map):
        """Test process_all_files() with workdir set. Tests negative of branch
        testing workdir. Verify process_file_map() called with expected
        arguments."""
        file_map = [StubFileMap()]
        mock_init_file_map.return_value = file_map
        mock_os_access.return_value = True
        process_all_files('.')
        mock_process_file_map.assert_called_with(file_map, None)

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @patch('photo_rename.process_file_map')
    @patch('photo_rename.init_file_map')
    @patch('photo_rename.os.path.exists')
    def test_process_all_files_exists_true(self, mock_os_path,
            mock_init_file_map,
            mock_process_file_map):
        """Test process_all_files() with workdir path exists True. Verify that
        process_file_map() called with correct arguments."""
        file_map = [StubFileMap()]
        mock_init_file_map.return_value = file_map
        mock_os_path.return_value = True
        process_all_files('.')
        mock_process_file_map.assert_called_with(file_map, None)

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @patch('photo_rename.os.path.exists')
    @patch('photo_rename.sys.exit')
    def test_process_all_files_exists_false(self, mock_sys_exit, mock_os_path):
        """Test process_all_files() with workdir path exists False. Tests
        positive branch of workdir not exists test. Verify that sys.exit() is
        called with expected argument."""
        mock_os_path.return_value = False
        process_all_files('.')
        mock_sys_exit.assert_called_with(1)

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @patch('photo_rename.process_file_map')
    @patch('photo_rename.init_file_map')
    @patch('photo_rename.os.access')
    def test_process_all_files_access_true(self, mock_os_access,
            mock_init_file_map, mock_process_file_map):
        """Test process_all_files() with workdir access True. Tests for
        negative branch of W_OK access test. Verify process_file_map() called
        with expected arguments."""
        file_map = [StubFileMap()]
        mock_init_file_map.return_value = file_map
        mock_os_access.return_value = True
        process_all_files('.')
        mock_process_file_map.assert_called_with(file_map, None)

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @patch('photo_rename.os.access')
    @patch('photo_rename.sys.exit')
    def test_process_all_files_access_false(self, mock_sys_exit,
            mock_os_access):
        """Test process_all_files() with workdir access False. Tests for
        positive branch of W_OK access test. Verify sys.exit() called with
        expected arguments."""
        mock_os_access.return_value = False
        process_all_files('.')
        mock_sys_exit.assert_called_with(1)