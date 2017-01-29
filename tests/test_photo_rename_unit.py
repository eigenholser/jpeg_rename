import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *

# Setup valid EXIF data with expected new filename
EXIF_DATA_VALID = {
    'exif_data': {
        'Exif.Image.DateTimeOriginal': '2014:08:26 06:20:20'
    },
}

EXIF_DATA_NOT_VALID = {'Exif.Image.DateTimeOriginal': '2014:08:26 06:20'}

expected_new_fn = re.sub(r':', r'',
        EXIF_DATA_VALID['exif_data']['Exif.Image.DateTimeOriginal'])
expected_new_fn = re.sub(r' ', r'_', expected_new_fn)
expected_new_fn = '{0}.jpg'.format(expected_new_fn)
EXIF_DATA_VALID['expected_new_fn'] = expected_new_fn

OLD_FN_JPG_LOWER = 'filename.jpg'
OLD_FN_JPG_UPPER = 'filename.JPG'
OLD_FN_JPEG = 'filename.jpeg'

SKIP_TEST = False

class TestGetNewFn():
    """Tests for method build_new_fn() are in this class."""
    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @pytest.mark.parametrize("old_fn,expected_new_fn,exif_data", [
        (OLD_FN_JPG_LOWER, EXIF_DATA_VALID['expected_new_fn'],
            EXIF_DATA_VALID['exif_data'],),
        (OLD_FN_JPG_LOWER, OLD_FN_JPG_LOWER, EXIF_DATA_NOT_VALID),
        (OLD_FN_JPG_LOWER, OLD_FN_JPG_LOWER, {},),
        (OLD_FN_JPEG, OLD_FN_JPG_LOWER, {},),
    ])
    def test_build_new_fn_parametrized_exif_data(self, old_fn, expected_new_fn,
            exif_data):
        """Test build_new_fn() with various EXIF data."""
        filemap = FileMap(old_fn, None, exif_data)
        new_fn = filemap.new_fn
        assert new_fn == expected_new_fn


class TestReadExifData():
    """Tests for method read_exif_data() are in this class."""
    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch.object(pyexiv2, 'ImageMetadata')
    def test_read_exif_data(self, mock_img_md):
        """Tests read_exif_data() with valid EXIF data. Tests for normal
        operation. Verify expected EXIF data in instantiated object."""

        class StubExifTag(object):
            raw_value = EXIF_DATA_VALID['exif_data']['Exif.Image.DateTimeOriginal']

        class TestImage(object):
            """
            ImageMetadata test stub.
            """
            def __getitem__(self, key):
                return StubExifTag()

            def read(self):
                return EXIF_DATA_VALID['exif_data']

            @property
            def exif_keys(self):
                return ['Exif.Image.DateTimeOriginal']


        old_fn = OLD_FN_JPG_LOWER
        mock_img_md.return_value = TestImage()
        filemap = FileMap(old_fn)
        assert filemap.exif_data == EXIF_DATA_VALID['exif_data']

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch.object(pyexiv2, 'ImageMetadata')
    def test_read_exif_data_info_none(self, mock_img_md):
        """
        Tests read_exif_data() with no EXIF data available. Tests for raised
        Exception. Verify expected exception message.
        """

        class TestImage(object):
            """
            ImageMetadata test stub.
            """
            def read(self):
                return None

            @property
            def exif_keys(self):
                return []

        old_fn = OLD_FN_JPG_LOWER
        mock_img_md.return_value = TestImage()
        with pytest.raises(Exception) as excinfo:
            filemap = FileMap(old_fn)
        assert str(excinfo.value) == "{0} has no EXIF data.".format(old_fn)


class TestMove():
    """Tess for method move() are in this class."""
    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.FileMap.make_new_fn_unique')
    @patch('photo_rename.os.rename')
    def test_move_orthodox(self, mock_os, mock_fn_unique):
        """Rename file with mocked os.rename. Verify called with args."""
        mock_fn_unique.return_value = None
        old_fn = OLD_FN_JPG_LOWER
        exif_data = EXIF_DATA_NOT_VALID
        filemap = FileMap(old_fn, avoid_collisions=None, exif_data=exif_data)
        new_fn = filemap.new_fn
        filemap.move()
        mock_os.assert_called_with(old_fn, new_fn)

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.FileMap.make_new_fn_unique')
    @patch('photo_rename.os.rename')
    def test_move_orthodox_rename_raises_exeption(self, mock_os,
            mock_fn_unique):
        """Rename file with mocked os.rename. Verify called with args."""
        mock_fn_unique.return_value = None
        mock_os.side_effect = OSError((1, "Just testing.",))
        old_fn = OLD_FN_JPG_LOWER
        exif_data = EXIF_DATA_NOT_VALID
        filemap = FileMap(old_fn, avoid_collisions=None, exif_data=exif_data)
        new_fn = filemap.new_fn
        filemap.move()
        mock_os.assert_called_with(old_fn, new_fn)

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.FileMap.make_new_fn_unique')
    @patch('photo_rename.os.rename')
    def test_move_orthodox_fn_unique_raises_exception(self, mock_os,
            mock_fn_unique):
        """Rename file with mocked os.rename. Verify called with args."""
        mock_fn_unique.side_effect = OSError((1, "Just testing.",))
        old_fn = OLD_FN_JPG_LOWER
        exif_data = EXIF_DATA_NOT_VALID
        filemap = FileMap(old_fn, avoid_collisions=None, exif_data=exif_data)
        new_fn = filemap.new_fn
        with pytest.raises(OSError):
            filemap.move()

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.FileMap.make_new_fn_unique')
    @patch('photo_rename.os.path.exists')
    def test_move_collision_detected(self, mock_exists, mock_fn_unique):
        """Move file with collision_detected simulating avoid_collisions=False.
        """
        mock_fn_unique.return_value = None
        mock_exists.return_value = True
        old_fn = OLD_FN_JPG_LOWER
        exif_data = {}
        filemap = FileMap(old_fn, avoid_collisions=None, exif_data=exif_data)
        filemap.collision_detected = True
        new_fn = filemap.new_fn
        filemap.move()
        assert new_fn == old_fn


class TestRename():
    """Tests for method build_new_fn() are in this class."""
    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.os.path.exists')
    def test_rename_empty_exif_data(self, mock_exists):
        """Make unique filename with empty EXIF data."""
        mock_exists.return_value = True
        old_fn = OLD_FN_JPG_LOWER
        exif_data = EXIF_DATA_NOT_VALID
        filemap = FileMap(old_fn, avoid_collisions=True, exif_data=exif_data)
        new_fn = filemap.new_fn
        filemap.make_new_fn_unique()
        assert filemap.new_fn == old_fn

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.os.path.exists')
    def test_rename_with_valid_exif_data_and_avoid_collisions(self,
            mock_exists):
        """Make unique new filename from valid EXIF data. Avoid collisions."""
        mock_exists.return_value = True
        old_fn = OLD_FN_JPG_LOWER
        exif_data = EXIF_DATA_VALID['exif_data']
        filemap = FileMap(old_fn, avoid_collisions=True, exif_data=exif_data)
        new_fn = filemap.new_fn
        filemap.MAX_RENAME_ATTEMPTS = 2
        with pytest.raises(Exception):
            filemap.make_new_fn_unique()
        assert filemap.new_fn == EXIF_DATA_VALID['expected_new_fn']

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.os.path.exists')
    def test_rename_with_valid_exif_data_and_no_avoid_collisions(self,
            mock_exists):
        """Make unique new filename from valid EXIF data. Do not avoid
        collisions."""
        mock_exists.return_value = True
        old_fn = OLD_FN_JPG_LOWER
        exif_data = EXIF_DATA_VALID['exif_data']
        filemap = FileMap(old_fn, avoid_collisions=False, exif_data=exif_data)
        new_fn = filemap.new_fn
        filemap.MAX_RENAME_ATTEMPTS = 2
        filemap.make_new_fn_unique()
        assert filemap.new_fn == EXIF_DATA_VALID['expected_new_fn']

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.os.path.exists')
    def test_rename_no_collision(self, mock_exists):
        """Make unique new filename from valid EXIF data. Do not avoid
        collisions."""
        mock_exists.return_value = False
        old_fn = OLD_FN_JPG_LOWER
        exif_data = {}
        filemap = FileMap(old_fn, avoid_collisions=False, exif_data=exif_data)
        new_fn = filemap.new_fn
        filemap.make_new_fn_unique()
        assert filemap.new_fn == old_fn


class TestInitFileMap():
    """Tests for function init_file_map() are in this class."""
    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.FileMap')
    @patch('photo_rename.glob')
    def test_init_file_map_orthodox(self, mock_glob, mock_filemap):
        """Tests init_file_map() list building. Verifies expected return value.
        """
        test_file_map = StubFileMap()
        mock_filemap.return_value = test_file_map
        mock_glob.glob.return_value = ['/foo/bar']
        file_map = init_file_map('.')
        assert file_map.file_map == [test_file_map,
                                     test_file_map,
                                     test_file_map]

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.FileMap')
    @patch('photo_rename.glob')
    def test_init_file_map_raises_exception(self, mock_glob, mock_filemap):
        """Tests init_file_map() with exception handling. Test exception raised
        when append to file_map list. Verify expected file_map returned."""
        mock_filemap.side_effect = Exception("Just testing.")
        mock_glob.glob.return_value = ['/foo/bar']
        file_map = init_file_map('.')
        assert file_map.file_map == []


class TestProcessFileMap():
    """Tests for function process_file_map() are in this class."""
    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    def test_process_file_map(self):
        """Test process_file_map()."""
        def move_func(old_fn, new_fn):
            pass

        file_map_list = FileMapList()
        file_map_list.add(StubFileMap())
        assert process_file_map(file_map_list, True, move_func) == None

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    def test_process_file_map_raise_exception(self):
        """Test exception handling in process_file_map()."""
        def move_func(old_fn, new_fn):
            raise Exception("Faux failure")
        file_map_list = FileMapList()
        file_map_list.add(StubFileMap())
        assert process_file_map(file_map_list, True, move_func) == None

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.FileMap')
    def test_process_file_map_simon_sez_false_fn_eq(self, mock_fm):
        """Test process_file_map() with simon_sez=False. Tests else branch with
        old_fn == new_fn. Verify same_files attribute value is True."""
        mock_fm.same_files = True
        mock_fm.old_fn = OLD_FN_JPG_LOWER
        mock_fm.new_fn = OLD_FN_JPG_LOWER
        file_map_list = FileMapList()
        file_map_list.add(mock_fm)
        process_file_map(file_map_list)
        assert mock_fm.same_files == True

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.FileMap')
    def test_process_file_map_simon_sez_false_fn_ne(self, mock_fm):
        """Test process_file_map() with simon_sez=False. Tests else branch with
        old_fn != new_fn. Verify same_files attribute value is False."""
        mock_fm.same_files = False
        mock_fm.old_fn = OLD_FN_JPG_LOWER
        mock_fm.new_fn = ''
        file_map_list = FileMapList()
        file_map_list.add(mock_fm)
        process_file_map(file_map_list)
        assert mock_fm.same_files == False

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.FileMap.move')
    @patch('photo_rename.FileMap')
    def test_process_file_map_simon_sez(self, mock_fm, mock_fm_move):
        """Call process_file_map with simon_sez=True, move_func=None. Tests
        call to move() method of FileMap instance when no test stub present and
        simon_sez True. Verify call to move() made as expected."""
        file_map_list = FileMapList()
        file_map_list.add(mock_fm)
        process_file_map(file_map_list, simon_sez=True)
        mock_fm.move.assert_called_with()


class TestProcessAllFiles():
    """Tests for the function process_all_files() are in this class."""
    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.init_file_map')
    @patch('photo_rename.os.access')
    @patch('photo_rename.os.path.dirname')
    @patch('photo_rename.os.path.exists')
    @patch('photo_rename.os.path.abspath')
    def test_process_all_files_workdir_none(self, mock_abspath, mock_exists,
            mock_dirname, mock_os_access, mock_init_file_map):
        """Test process_all_files() with workdir=None, avoid_collisions=None.
        Verify that init_file_map() is called with (DIRNAME, None)."""
        DIRNAME = '/foo/bar'
        mock_abspath.return_value = DIRNAME
        mock_exists.return_value = True
        mock_dirname.return_value = DIRNAME
        process_all_files()
        mock_init_file_map.assert_called_with(DIRNAME, None)

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
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

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
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

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.os.path.exists')
    @patch('photo_rename.sys.exit')
    def test_process_all_files_exists_false(self, mock_sys_exit, mock_os_path):
        """Test process_all_files() with workdir path exists False. Tests
        positive branch of workdir not exists test. Verify that sys.exit() is
        called with expected argument."""
        mock_os_path.return_value = False
        process_all_files('.')
        mock_sys_exit.assert_called_with(1)

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
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

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
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


class TestFileMapList(object):
    """Tests for FileMapList."""

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    def test_file_map_list_init(self):
        """Instantiate FileMapList() and test __init__() method. Verify
        file_map is initialized to empty list."""
        file_map_list = FileMapList()
        assert file_map_list.file_map == []

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
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

            return Args()

    @pytest.mark.skipif(SKIP_TEST, reason="Work in progress")
    @patch('photo_rename.argparse.ArgumentParser', TestArgumentParser)
    @patch('photo_rename.process_all_files')
    def test_main_function(self, mock_process_all_files):
        """Test main() function. Mock argparse and replace with stubs. Verify
        process_all_files called with expected arguments."""
        mock_process_all_files.return_value = 1234
        retval = main()
        mock_process_all_files.assert_called_with(workdir='.', simon_sez=False,
                avoid_collisions=False)


class StubFileMap(object):
    """Stub to be used in place of FileMap()."""

    def __init__(self):
        self.old_fn = 'foo.jpg'
        self.new_fn = 'bar.jpg'

