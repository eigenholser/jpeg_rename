import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from stubs import *


class TestFileMapList(object):
    """Tests for FileMapList."""

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    def test_file_map_list_init(self):
        """Instantiate FileMapList() and test __init__() method. Verify
        file_map is initialized to empty list."""
        file_map_list = FileMapList()
        assert file_map_list.file_map == []

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    def test_file_map_list_add(self):
        """Tests FileMapList add() method. Adds multiple FileMap instances
        and verifies expected ordering of instances based on new_fn attribute.
        """
        test_file_map_1 = StubFileMap()
        test_file_map_2 = StubFileMap()
        test_file_map_2.new_fn = 'aaa.jpg'
        file_map_list = FileMapList()
        file_map_list.add(test_file_map_1)
        file_map_list.add(test_file_map_2)
        assert file_map_list.file_map == [test_file_map_2, test_file_map_1]
