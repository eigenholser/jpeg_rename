import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename.rename import *
from .stubs import *
from . import TEST_RENAME_PROCESS_ALL_FILES


class TestRenameProcessAllFiles(object):
    """
    Tests for the function process_all_files() are in this class.
    """
    skiptests = not TEST_RENAME_PROCESS_ALL_FILES

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.rename.Harvester')
    @patch('photo_rename.rename.sys.exit')
    @patch('photo_rename.rename.os.path.exists')
    @patch('photo_rename.rename.os.access')
    def test_process_all_files_exists_and_access(self, m_os_access,
            m_os_path_exists, m_sys_exit, m_harvey):
        """
        Test process_all_files() with workdir set. Tests negative of branch
        testing workdir. Verify os.path.exists() and os.access() called with
        proper arguments. Verify sys.exit() not called.
        """
        file_map = [StubFilemap()]
        m_harvey.__getitem__.return_value = file_map
        m_harvey.process_file_map.return_value = None
        m_os_path_exists.return_value = True
        m_os_access.return_value = True
        process_all_files('.')
        m_os_path_exists.assert_called_with(".")
        m_os_access.assert_called_with('.', os.W_OK)
        m_sys_exit.assert_not_called()

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.rename.Harvester')
    @patch('photo_rename.rename.sys.exit')
    @patch('photo_rename.rename.os.path.exists')
    @patch('photo_rename.rename.os.access')
    def test_process_all_files_exists_and_not_access(self, m_os_access,
            m_os_path_exists, m_sys_exit, m_harvey):
        """
        Test process_all_files() with workdir path exists. Verify that
        os.path.exists() called with ".", os_access() not called, and
        sys.exit() called with 1.
        """
        file_map = [StubFilemap()]
        m_harvey.__getitem__.return_value = file_map
        m_harvey.process_file_map.return_value = None
        m_os_path_exists.return_value = True
        m_os_access.return_value = False
        process_all_files('.')
        m_os_path_exists.assert_called_with(".")
        m_os_access.assert_called_with(".", os.W_OK)
        m_sys_exit.assert_called_with(1)
        m_sys_exit.assert_called_once()

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.rename.Harvester')
    @patch('photo_rename.rename.sys.exit')
    @patch('photo_rename.rename.os.path.exists')
    @patch('photo_rename.rename.os.access')
    def test_process_all_files_not_exists_and_access(self, m_os_access,
            m_os_path_exists, m_sys_exit, m_harvey):
        """
        Test process_all_files() with workdir path exists False. Verify that
        os.path.exists() called with ".", os_access() not called, and
        sys.exit() called with 1 and only once.
        """
        file_map = [StubFilemap()]
        m_harvey.__getitem__.return_value = file_map
        m_harvey.process_file_map.return_value = None
        m_os_path_exists.return_value = False
        m_os_access.return_value = True
        process_all_files('.')
        m_os_path_exists.assert_called_with(".")
        m_os_access.assert_called_with(".", os.W_OK)
        m_sys_exit.assert_called_with(1)
        m_sys_exit.assert_called_once()

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.rename.Harvester')
    @patch('photo_rename.rename.sys.exit')
    @patch('photo_rename.rename.os.path.exists')
    @patch('photo_rename.rename.os.access')
    def test_process_all_files_harvey_args(self, m_os_access,
            m_os_path_exists, m_sys_exit, m_harvey):
        """
        Test process_all_files() with workdir set. Tests negative of branch
        testing workdir. Verify os.path.exists() and os.access() called with
        proper arguments. Verify sys.exit() not called. Primarily, test that
        harvester and process_file_map() args correct.
        """
        def pfm(fm, ss):
            pass

        file_map = [StubFilemap()]
        m_harvey.__getitem__.return_value = file_map
        m_os_path_exists.return_value = True
        m_os_access.return_value = True
        process_all_files('.')
        m_os_path_exists.assert_called_with(".")
        m_os_access.assert_called_with('.', os.W_OK)
        m_sys_exit.assert_not_called()
        m_harvey.assert_called_with(".", None)


