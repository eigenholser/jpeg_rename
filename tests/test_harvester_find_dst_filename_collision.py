import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

import photo_rename
from photo_rename.rename import *
from .stubs import *
from . import TEST_HARVESTER_FIND_DST_FILENAME_COLLISION


class TestFindDstFilenameCollision(object):
    """
    Tests for Harvester.find_dst_filename_collision() method.
    """
    skiptests = not TEST_HARVESTER_FIND_DST_FILENAME_COLLISION

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.FilemapList')
    @patch('photo_rename.harvester.Filemap')
    def test_filename_collision(
            self, m_filemap, m_filemaplist):
        """
        Test find_dst_filename_collision() method. Arrange for filename
        collision. Confirm it is renamed as expected.
        """
        files = [
            '19991231_000001.jpg',
            '19991231_000001.png',
            '19991231_000001.arw',
            '19991231_000001.tif',
            '19991231_000001.xyz',
        ]
        dst_fn_expected = '19991231_000001-1.jpg'
        filemap1 = Mock()
        filemap1.dst_fn = files[0]
        filemap2 = Mock()
        filemap2.dst_fn = files[1]
        filemap3 = Mock()
        filemap3.dst_fn = files[0]
        filemaps = [
            filemap1,
            filemap2,
            filemap3,
        ]
        attrs = {'get.return_value': filemaps}
        m_filemaplist.configure_mock(**attrs)
        harvey = Harvester('.')
        dst_fn = harvey.find_dst_filename_collision(m_filemaplist, filemap3)
        assert dst_fn == dst_fn_expected

