import os
import re
import sys
import pytest
from mock import Mock, mock_open, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from stubs import *

@pytest.fixture
def alt_file_map_tab():
    """
    Sample alternate file map.
    """
    return """
abc 123	MY NEW FILE 1
xyz 999	MY NEW FILE 2
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
def alt_file_map_dict():
    """
    Sample alternate file map converted to dict.
    """
    return {"abc 123": "MY NEW FILE 1", "xyz 999": "MY NEW FILE 2"}

class TestFilemapReadAltFilemap(object):
    """
    Tests reading alternate file map.
    """

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    def test_read_alt_file_map(self, alt_file_map_tab, alt_file_map_dict):
        """
        Read alt file map and create dict with default delimiter `\t'.
        """
        a = mock_open(read_data=alt_file_map_tab.strip())
        with patch('builtins.open', a) as m:
            afmd = read_alt_file_map("foo")
            assert afmd == alt_file_map_dict

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    def test_read_alt_file_map(self, alt_file_map_xxx, alt_file_map_dict):
        """
        Read alt file map and create dict with custom delimiter `xxx'.
        """
        a = mock_open(read_data=alt_file_map_xxx.strip())
        with patch('builtins.open', a) as m:
            afmd = read_alt_file_map("foo", delimiter="xxx")
            assert afmd == alt_file_map_dict

