import os
import re
import sys
import pytest
from mock import Mock, mock_open, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from .stubs import *
from . import (
        TEST_FILEMAP_READ_ALT_FILE_MAP,
        TEST_FILEMAP_GET_LINE_TERM,
        TEST_FILEMAP_SCAN_FOR_DUPE_FILES,
    )


@pytest.fixture
def alt_file_map_tab():
    """
    Sample alternate file map.
    """
    return """
abc 123	MY NEW FILE 1
xyz 999	MY NEW FILE 2
# this is a comment
    """


@pytest.fixture
def alt_file_map_duplicate_source():
    """
    Alternate file map with duplicate source filenames.
    """
    return """
abc 123	MY NEW FILE 1
abc 123	MY NEW FILE 2
    """


@pytest.fixture
def alt_file_map_duplicate_dest():
    """
    Alternate file map with duplicate dest filenames.
    """
    return """
abc 123	MY NEW FILE 1
xyz 999	MY NEW FILE 1
    """


@pytest.fixture
def alt_file_map_xxx():
    """
    Sample alternate file map.
    """
    return """
abc 123xxxMY NEW FILE 1
xyz 999xxxMY NEW FILE 2
    """


@pytest.fixture
def alt_file_map_term_crlf():
    """
    Sample alternate file map with DOS line endings.
    """
    return """abc 123\tMY NEW FILE 1\r\nxyz 999\tMY NEW FILE 2\r\n"""


@pytest.fixture
def alt_file_map_term_mixed():
    """
    Sample alternate file map with DOS line endings.
    """
    return """abc 123\tMY NEW FILE 1\nxyz 999\tMY NEW FILE 2\r\n"""


@pytest.fixture
def alt_file_map_dict():
    """
    Sample alternate file map converted to dict.
    """
    return {"abc 123": "MY NEW FILE 1", "xyz 999": "MY NEW FILE 2"}


class TestFilemapReadAltFileMap(object):
    """
    Tests reading alternate file map.
    """
    skiptests = not TEST_FILEMAP_READ_ALT_FILE_MAP

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.get_line_term')
    @patch('photo_rename.scan_for_dupe_files')
    def test_read_alt_file_map(self, m_scan_for_dupe_files, m_get_line_term,
            alt_file_map_tab, alt_file_map_dict):
        """
        Read alt file map and create dict with default delimiter `\t' and
        Unix line termination.
        """
        a = mock_open(read_data=alt_file_map_tab.strip())
        m_get_line_term.return_value = '\n'
        m_scan_for_dupe_files.return_value = False
        with patch('builtins.open', a) as m:
            afmd = read_alt_file_map("foo")
            assert afmd == alt_file_map_dict

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.scan_for_dupe_files')
    def test_read_alt_file_map_crlf(self, m_scan_for_dupe_files,
            alt_file_map_term_crlf, alt_file_map_dict):
        """
        Read alt file map and create dict with default delimiter `\t' and
        DOS line termination. Skip lineterm branch.
        """
        a = mock_open(read_data=alt_file_map_term_crlf.strip())
        m_scan_for_dupe_files.return_value = False
        with patch('builtins.open', a) as m:
            afmd = read_alt_file_map("foo", lineterm='\r\n')
            assert afmd == alt_file_map_dict

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.scan_for_dupe_files')
    def test_read_alt_file_map_duplicate_source(self, m_scan_for_dupe_files,
            alt_file_map_duplicate_source, alt_file_map_dict):
        """
        Read alt file map with duplicate source filenames.
        """
        # TODO: don't hardwire assert
        a = mock_open(read_data=alt_file_map_duplicate_source.strip())
        m_scan_for_dupe_files.return_value = False
        with patch('builtins.open', a) as m:
            afmd = read_alt_file_map("foo", lineterm='\n')
            assert afmd == {'abc 123': 'MY NEW FILE 2'}

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.get_line_term')
    @patch('photo_rename.scan_for_dupe_files')
    def test_read_alt_file_map_duplicate_dest(self, m_scan_for_dupe_files,
            get_line_term, alt_file_map_duplicate_dest, alt_file_map_dict):
        """
        Read alt file map with mocked duplicate dest filenames.
        """
        # No need to mock get_line_term() because we're passing in lineterm.
        a = mock_open(read_data=alt_file_map_duplicate_dest.strip())
        m_scan_for_dupe_files.return_value = True
        with patch('builtins.open', a) as m:
            with pytest.raises(Exception):
                afmd = read_alt_file_map("foo", lineterm='\n')

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.scan_for_dupe_files')
    def test_read_alt_file_map(self, m_scan_for_dupe_files, alt_file_map_xxx,
            alt_file_map_dict):
        """
        Read alt file map and create dict with custom delimiter `xxx'.
        """
        a = mock_open(read_data=alt_file_map_xxx.strip())
        m_scan_for_dupe_files.return_value = False
        with patch('builtins.open', a) as m:
            afmd = read_alt_file_map("foo", delimiter="xxx")
            assert afmd == alt_file_map_dict


class TestFilemapGetLineTerm(object):
    """
    Tests for function get_line_term().
    """
    skiptests = not TEST_FILEMAP_GET_LINE_TERM

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    def test_get_line_term_lf(self, alt_file_map_tab):
        """
        Read filemap with LF terminated lines.
        """
        a = mock_open(read_data=alt_file_map_tab)
        with patch('builtins.open', a) as m:
            with open('foo', 'r') as f:
                lines = [line for line in f.readlines()
                        if not line.startswith('#')]
        lineterm = get_line_term(lines)
        assert lineterm == '\n'

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    def test_get_line_term_mixed(self, alt_file_map_term_mixed):
        """
        Raises Exception with mixed line terminations.
        """
        a = mock_open(read_data=alt_file_map_term_mixed)
        with patch('builtins.open', a) as m:
            with open('foo', 'r') as f:
                lines = [line for line in f.readlines()
                        if not line.startswith('#')]
        with pytest.raises(Exception):
            lineterm = get_line_term(lines)


class TestFilemapScanForDupeFiles(object):
    """
    Tests for function scan_for_dupe_files().
    """
    skiptests = not TEST_FILEMAP_SCAN_FOR_DUPE_FILES

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    def test_scan_for_dupe_files_unique(self):
        """
        Test with unique filenames. Confirm False result.
        """
        files = ['abc', 'def']
        assert scan_for_dupe_files(files) == False

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    def test_scan_for_dupe_files_duplicate(self):
        """
        Test with duplicate filenames. Confirm True result.
        """
        files = ['abc', 'abc']
        assert scan_for_dupe_files(files) == True


