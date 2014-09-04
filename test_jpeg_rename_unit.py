import os
import sys
sys.path.append('..')
import pytest
from mock import Mock, patch
from jpeg_rename import *

# Setup valid EXIF data with expected new filename
EXIF_DATA_VALID = {
    'exif_data': {
        'DateTimeOriginal': '2014:08:26 06:20:20'
    },
}

EXIF_DATA_NOT_VALID = {'DateTimeOriginal': '2014:08:26 06:20'}

expected_new_fn = re.sub(r':', r'',
        EXIF_DATA_VALID['exif_data']['DateTimeOriginal'])
expected_new_fn = re.sub(r' ', r'_', expected_new_fn)
expected_new_fn = '{0}.jpg'.format(expected_new_fn)
EXIF_DATA_VALID['expected_new_fn'] = expected_new_fn

OLD_FN_JPG_LOWER = 'filename.jpg'
OLD_FN_JPG_UPPER = 'filename.JPG'
OLD_FN_JPEG = 'filename.jpeg'

#@pytest.mark.skipif('True', reason="Work in progress")
@pytest.mark.parametrize("old_fn,expected_new_fn,exif_data", [
    (OLD_FN_JPG_LOWER, EXIF_DATA_VALID['expected_new_fn'],
        EXIF_DATA_VALID['exif_data'],),
    (OLD_FN_JPG_LOWER, OLD_FN_JPG_LOWER, EXIF_DATA_NOT_VALID),
    (OLD_FN_JPG_LOWER, OLD_FN_JPG_LOWER, {},),
    (OLD_FN_JPEG, OLD_FN_JPG_LOWER, {},),
])
def test_get_new_fn_parametrized_exif_data(old_fn, expected_new_fn, exif_data):
    """Test get_new_fn() with various EXIF data."""
    filemap = FileMap(old_fn, None, exif_data)
    new_fn = filemap.new_fn
    assert new_fn == expected_new_fn

# Contrast with parametrized version
@pytest.mark.skipif('True', reason="Work in progress")
def test_get_new_fn_with_invalid_exif_data():
    """Test get_new_fn() with invalid EXIF data."""

    exif_data = EXIF_DATA_NOT_VALID
    old_fn = OLD_FN_JPG_LOWER
    filemap = FileMap(old_fn, None, exif_data)
    new_fn = filemap.new_fn
    assert old_fn == new_fn

# Contrast with parametrized version
@pytest.mark.skipif('True', reason="Work in progress")
def test_get_new_fn_with_no_exif_data():
    """Test get_new_fn() with no EXIF data and old_fn with correct file
    extension."""
    exif_data = {}
    old_fn = OLD_FN_JPG_LOWER
    filemap = FileMap(old_fn, None, exif_data)
    new_fn = filemap.new_fn
    assert old_fn == new_fn

# Contrast with parametrized version
@pytest.mark.skipif('True', reason="Work in progress")
def test_get_new_fn_with_exif_data_and_wrong_ext():
    """Test get_new_fn() with valid EXIF data and wrong file extension."""
    exif_data = EXIF_DATA_VALID['exif_data']
    old_fn = OLD_FN_JPEG
    filemap = FileMap(old_fn, None, exif_data)
    new_fn = filemap.new_fn
    assert new_fn == EXIF_DATA_VALID['expected_new_fn']

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.TAGS')
@patch.object(Image, 'open')
def test_get_exif_data(mock_img, mock_tags):
    """
    """
    class TestImage():
        def _getexif(self):
            return EXIF_DATA_VALID['exif_data']

    def get(arg1, arg2):
        return 'DateTimeOriginal'

    old_fn = 'abc123.jpg'
    mock_img.return_value = TestImage()
    mock_tags.get = get
    filemap = FileMap(old_fn)
    assert filemap.exif_data == EXIF_DATA_VALID['exif_data']

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.TAGS')
@patch.object(Image, 'open')
def test_get_exif_data_info_none(mock_img, mock_tags):
    """
    """
    class TestImage():
        def _getexif(self):
            return None

    def get(arg1, arg2):
        return 'DateTimeOriginal'

    old_fn = 'abc123.jpg'
    mock_img.return_value = TestImage()
    mock_tags.get = get
    with pytest.raises(Exception) as excinfo:
        filemap = FileMap(old_fn)

    assert excinfo.value[0] == "{0} has no EXIF data.".format(old_fn)

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.FileMap.make_new_fn_unique')
@patch('jpeg_rename.os.rename')
def test_move_orthodox(mock_os, mock_fn_unique):
    """Rename file with mocked os.rename. Verify called with args."""
    mock_fn_unique.return_value = None
    old_fn = OLD_FN_JPG_LOWER
    exif_data = EXIF_DATA_NOT_VALID
    filemap = FileMap(old_fn, avoid_collisions=None, exif_data=exif_data)
    new_fn = filemap.new_fn
    filemap.move()
    mock_os.assert_called_with(old_fn, new_fn)

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.FileMap.make_new_fn_unique')
@patch('jpeg_rename.os.rename')
def test_move_orthodox_rename_raises_exeption(mock_os, mock_fn_unique):
    """Rename file with mocked os.rename. Verify called with args."""
    mock_fn_unique.return_value = None
    mock_os.side_effect = OSError((1, "Just testing.",))
    old_fn = OLD_FN_JPG_LOWER
    exif_data = EXIF_DATA_NOT_VALID
    filemap = FileMap(old_fn, avoid_collisions=None, exif_data=exif_data)
    new_fn = filemap.new_fn
    filemap.move()
    mock_os.assert_called_with(old_fn, new_fn)

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.FileMap.make_new_fn_unique')
@patch('jpeg_rename.os.rename')
def test_move_orthodox_fn_unique_raises_exception(mock_os, mock_fn_unique):
    """Rename file with mocked os.rename. Verify called with args."""
    mock_fn_unique.side_effect = OSError((1, "Just testing.",))
    old_fn = OLD_FN_JPG_LOWER
    exif_data = EXIF_DATA_NOT_VALID
    filemap = FileMap(old_fn, avoid_collisions=None, exif_data=exif_data)
    new_fn = filemap.new_fn
    with pytest.raises(OSError):
        filemap.move()

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.FileMap.make_new_fn_unique')
@patch('jpeg_rename.os.path.exists')
def test_move_collision_detected(mock_exists, mock_fn_unique):
    """Move file with collision_detected simulating avoid_collisions = False.
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

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.os.path.exists')
def test_rename_empty_exif_data(mock_exists):
    """Make unique filename with empty EXIF data."""
    mock_exists.return_value = True
    old_fn = OLD_FN_JPG_LOWER
    exif_data = EXIF_DATA_NOT_VALID
    filemap = FileMap(old_fn, avoid_collisions=True, exif_data=exif_data)
    new_fn = filemap.new_fn
    filemap.make_new_fn_unique()
    assert filemap.new_fn == old_fn

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.os.path.exists')
def test_rename_with_valid_exif_data_and_avoid_collisions(mock_exists):
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

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.os.path.exists')
def test_rename_with_valid_exif_data_and_no_avoid_collisions(mock_exists):
    """Make unique new filename from valid EXIF data. Do not avoid collisions.
    """
    mock_exists.return_value = True
    old_fn = OLD_FN_JPG_LOWER
    exif_data = EXIF_DATA_VALID['exif_data']
    filemap = FileMap(old_fn, avoid_collisions=False, exif_data=exif_data)
    new_fn = filemap.new_fn
    filemap.MAX_RENAME_ATTEMPTS = 2
    filemap.make_new_fn_unique()
    assert filemap.new_fn == EXIF_DATA_VALID['expected_new_fn']

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.os.path.exists')
def test_rename_no_collision(mock_exists):
    """Make unique new filename from valid EXIF data. Do not avoid collisions.
    """
    mock_exists.return_value = False
    old_fn = OLD_FN_JPG_LOWER
    exif_data = {}
    filemap = FileMap(old_fn, avoid_collisions=False, exif_data=exif_data)
    new_fn = filemap.new_fn
    filemap.make_new_fn_unique()
    assert filemap.new_fn == old_fn

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.FileMap')
@patch('jpeg_rename.glob')
def test_init_file_map_orthodox(mock_glob, mock_filemap):
    """Tests init_file_map() list building. Verifies expected return value."""
    mock_filemap.return_value = True
    mock_glob.glob.return_value = ['/foo/bar']
    file_map = init_file_map('.')
    assert file_map == [True, True, True]

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.FileMap')
@patch('jpeg_rename.glob')
def test_init_file_map_raises_exception(mock_glob, mock_filemap):
    """Tests init_file_map() with exception handling. Test exception raised
    when append to file_map list. Verify expected file_map returned."""
    mock_filemap.side_effect = Exception("Just testing.")
    mock_glob.glob.return_value = ['/foo/bar']
    file_map = init_file_map('.')
    assert file_map == []

##
## process_file_map() tests
##

#@pytest.mark.skipif('True', reason="Work in progress")
def test_process_file_map():
    """Test process_file_map()."""
    def move_func(old_fn, new_fn):
        pass

    assert process_file_map([TestFileMap()], True, move_func) == None

#@pytest.mark.skipif('True', reason="Work in progress")
def test_process_file_map_raise_exception():
    """Test exception handling in process_file_map()."""
    def move_func(old_fn, new_fn):
        raise Exception("Faux failure")
    assert process_file_map([TestFileMap()], True, move_func) == None

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.FileMap')
def test_process_file_map_simon_sez_false_fn_eq(mock_fm):
    """Test process_file_map() with simon_sez=False. Tests else branch with
    old_fn == new_fn. Verify same_files attribute value is True."""
    mock_fm.same_files = True
    mock_fm.old_fn = 'abc123.jpg'
    mock_fm.new_fn = 'abc123.jpg'
    file_map = [mock_fm]
    process_file_map(file_map)
    assert mock_fm.same_files == True

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.FileMap')
def test_process_file_map_simon_sez_false_fn_ne(mock_fm):
    """Test process_file_map() with simon_sez=False. Tests else branch with
    old_fn != new_fn. Verify same_files attribute value is False."""
    mock_fm.same_files = False
    mock_fm.old_fn = 'abc123.jpg'
    mock_fm.new_fn = ''
    file_map = [mock_fm]
    process_file_map(file_map)
    assert mock_fm.same_files == False

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.FileMap.move')
@patch('jpeg_rename.FileMap')
def test_process_file_map_simon_sez(mock_fm, mock_fm_move):
    """Call process_file_map with simon_sez=True, move_func=None. Tests call to
    move() method of FileMap instance when no test stub present and simon_sez
    True. Verify call to move() made as expected."""
    file_map = [mock_fm]
    process_file_map(file_map, simon_sez=True)
    mock_fm.move.assert_called_with()

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.init_file_map')
@patch('jpeg_rename.os.access')
@patch('jpeg_rename.os.path.dirname')
@patch('jpeg_rename.os.path.exists')
@patch('jpeg_rename.os.path.abspath')
def test_process_all_files_workdir_none(mock_abspath, mock_exists,
        mock_dirname, mock_os_access, mock_init_file_map):
    """Test process_all_files() with workdir=None, avoid_collisions=None.
    Verify that init_file_map() is called with (DIRNAME, None)."""
    DIRNAME = '/foo/bar'
    mock_abspath.return_value = DIRNAME
    mock_exists.return_value = True
    mock_dirname.return_value = DIRNAME
    process_all_files()
    mock_init_file_map.assert_called_with(DIRNAME, None)

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.process_file_map')
@patch('jpeg_rename.init_file_map')
@patch('jpeg_rename.os.access')
def test_process_all_files_workdir_not_none(mock_os_access, mock_init_file_map,
        mock_process_file_map):
    """Test process_all_files() with workdir set. Tests negative of branch
    testing workdir. Verify process_file_map() called with expected arguments.
    """
    file_map = [TestFileMap()]
    mock_init_file_map.return_value = file_map
    mock_os_access.return_value = True
    process_all_files('.')
    mock_process_file_map.assert_called_with(file_map, None)

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.process_file_map')
@patch('jpeg_rename.init_file_map')
@patch('jpeg_rename.os.path.exists')
def test_process_all_files_exists_true(mock_os_path, mock_init_file_map,
        mock_process_file_map):
    """Test process_all_files() with workdir path exists True. Verify that
    process_file_map() called with correct arguments."""
    file_map = [TestFileMap()]
    mock_init_file_map.return_value = file_map
    mock_os_path.return_value = True
    process_all_files('.')
    mock_process_file_map.assert_called_with(file_map, None)

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.os.path.exists')
@patch('jpeg_rename.sys.exit')
def test_process_all_files_exists_false(mock_sys_exit, mock_os_path):
    """Test process_all_files() with workdir path exists False. Tests positive
    branch of workdir not exists test. Verify that sys.exit() is called with
    expected argument."""
    mock_os_path.return_value = False
    process_all_files('.')
    mock_sys_exit.assert_called_with(1)

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.process_file_map')
@patch('jpeg_rename.init_file_map')
@patch('jpeg_rename.os.access')
def test_process_all_files_access_true(mock_os_access, mock_init_file_map,
        mock_process_file_map):
    """Test process_all_files() with workdir access True. Tests for negative
    branch of W_OK access test. Verify process_file_map() called with expected
    arguments."""
    file_map = [TestFileMap()]
    mock_init_file_map.return_value = file_map
    mock_os_access.return_value = True
    process_all_files('.')
    mock_process_file_map.assert_called_with(file_map, None)

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.os.access')
@patch('jpeg_rename.sys.exit')
def test_process_all_files_access_false(mock_sys_exit, mock_os_access):
    """Test process_all_files() with workdir access False. Tests for positive
    branch of W_OK access test. Verify sys.exit() called with expected
    arguments."""
    mock_os_access.return_value = False
    process_all_files('.')
    mock_sys_exit.assert_called_with(1)


class TestFileMap():

    def __init__(self):
        self.old_fn = 'foo.jpg'
        self.new_fn = 'bar.jpg'

