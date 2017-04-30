import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import FilemapList
from photo_rename.rename import *
from .stubs import *
from . import TEST_FILEMAP_LIST


class TestFilemapList(object):
    """
    Tests for FilemapList.
    """
    skiptests = not TEST_FILEMAP_LIST

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    def test_file_map_list_init(self):
        """
        Instantiate FilemapList() and test __init__() method. Verify
        file_map is initialized to empty list.
        """
        filemaps = FilemapList()
        assert [fm for fm in filemaps.get()] == []

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    def test_file_map_list_add(self):
        """
        Tests FilemapList add() method. Adds multiple Filemap instances
        and verifies expected ordering of instances based on dst_fn attribute.
        """
        test_file_map_1 = StubFilemap()
        test_file_map_2 = StubFilemap()
        test_file_map_2.dst_fn = 'aaa.jpg'
        filemaps = FilemapList()
        filemaps.add(test_file_map_1)
        filemaps.add(test_file_map_2)
        assert [fm for fm in filemaps.get()] == [test_file_map_2, test_file_map_1]

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    def test_filemaplist_add_dated_with_same_and_seq(self):
        """
        Tests FilemapList add() method. Adds files named with YYYYmmdd_HHMMSS
        to list containing files named YYYYmmdd_HHMMSS-dd where
        YYYmmdd_HHMMSS is same. Verify proper insertion order.
        """
        # These filename chosen to hit the important cases.
        test_file1 = "19991231_235957.png"
        test_file2 = "19991231_235958.png"
        test_file3 = "19991231_235958-1.png"
        test_file4 = "19991231_235958-2.png"
        test_file5 = "19991231_235958-3.png"
        test_file6 = "19991231_235959.png"
        filemaps = FilemapList()
        # This order chosen carefully to hit the branches properly.
        filemaps.add(test_file1)
        filemaps.add(test_file3)
        filemaps.add(test_file2)
        filemaps.add(test_file5)
        filemaps.add(test_file6)
        filemaps.add(test_file4)
        assert [file for file in filemaps.get()] == [test_file1, test_file2,
                test_file3, test_file4, test_file5, test_file6]

