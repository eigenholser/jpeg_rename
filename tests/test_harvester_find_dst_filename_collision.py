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
    def test_filename_collision_resolution(
            self, m_filemap, m_filemaplist):
        """
        Test find_dst_filename_collision() method. Arrange for filename
        collision. Confirm file is renamed as expected.
        """
        files = [
            '19991231_000009.jpg',
            '19991231_000001.jpg',
            '19991231_000001-1.jpg',
            '19991231_000003.jpg',
            '19991231_000001.jpg',
            '19991231_000002.arw',
            '19991231_000001.tif',
            '19991231_000001.xyz',
        ]
        dst_fn_expected = '19991231_000001-2.jpg'
        filemap1 = Mock()
        filemap1.dst_fn = files[1]
        filemap2 = Mock()
        filemap2.dst_fn = files[2]
        filemap3 = Mock()
        filemap3.dst_fn = files[1]
        filemap4 = Mock()
        filemap4.dst_fn = files[3]
        filemap5 = Mock()
        filemap5.dst_fn = files[4]
        filemaps = [
            filemap1,
            filemap2,
            filemap3,
            filemap4,
            filemap5,
        ]
        attrs = {'get.return_value': filemaps}
        m_filemaplist.configure_mock(**attrs)
        harvey = Harvester('.')
        #import pdb; pdb.set_trace()
        dst_fn = harvey.find_dst_filename_collision(m_filemaplist, filemap5)
        assert dst_fn == dst_fn_expected

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.harvester.FilemapList')
    @patch('photo_rename.harvester.Filemap')
    def test_filename_collision_max_rename_attempts_exception(
            self, m_filemap, m_filemaplist):
        """
        Test find_dst_filename_collision() method. Arrange for repeated
        filename collisions until MAX_RENAME_ATTEMPTS is exceeded. Confirm it
        Exception is raised with correct message.
        """
        files = [
            '19991231_000001.jpg',
            '19991231_000001-1.jpg',
            '19991231_000001-2.jpg',
            '19991231_000001-3.jpg',
            '19991231_000001-4.jpg',
            '19991231_000001-5.jpg',
            '19991231_000001-6.jpg',
            '19991231_000001-7.jpg',
            '19991231_000001-8.jpg',
            '19991231_000001-9.jpg',
            '19991231_000001-10.jpg',
            '19991231_000001.jpg',
        ]
        dst_fn_expected = '19991231_000001-2.jpg'
        filemap0 = Mock()
        filemap0.dst_fn = files[0]
        filemap1 = Mock()
        filemap1.dst_fn = files[1]
        filemap2 = Mock()
        filemap2.dst_fn = files[2]
        filemap3 = Mock()
        filemap3.dst_fn = files[3]
        filemap4 = Mock()
        filemap4.dst_fn = files[4]
        filemap5 = Mock()
        filemap5.dst_fn = files[5]
        filemap6 = Mock()
        filemap6.dst_fn = files[6]
        filemap7 = Mock()
        filemap7.dst_fn = files[7]
        filemap8 = Mock()
        filemap8.dst_fn = files[8]
        filemap9 = Mock()
        filemap9.dst_fn = files[9]
        filemap10 = Mock()
        filemap10.dst_fn = files[10]
        filemap11 = Mock()
        filemap11.dst_fn = files[11]
        filemaps = [
            filemap0,
            filemap1,
            filemap2,
            filemap3,
            filemap4,
            filemap5,
            filemap6,
            filemap7,
            filemap8,
            filemap9,
            filemap10,
            filemap11,
        ]
        attrs = {'get.return_value': filemaps}
        m_filemaplist.configure_mock(**attrs)
        harvey = Harvester('.')
        with pytest.raises(Exception) as excinfo:
            dst_fn_actual = harvey.find_dst_filename_collision(
                    m_filemaplist, filemap11)
        assert excinfo.value.args[0].startswith("Too many rename attempts")

