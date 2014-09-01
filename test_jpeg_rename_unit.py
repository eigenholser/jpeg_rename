import pytest
from mock import Mock, patch
from jpeg_rename import *

def test_process_file_map():
    """Test process_file_map()."""
    def move_func(old_fn, new_fn):
        pass

    assert process_file_map([TestFileMap()], True, move_func) == None


def test_process_file_map_raise_exception():
    """Test exception handling in process_file_map()."""
    def move_func(old_fn, new_fn):
        raise Exception("Faux failure")
    assert process_file_map([TestFileMap()], True, move_func) == None


def test_get_new_fn_with_invalid_exif_data():
    """Test get_new_fn() with invalid EXIF data."""

    exif_data = {'DateTimeOriginal': '2014:08:16 06:20'}
    old_fn = 'abc123.jpg'
    filemap = FileMap(old_fn, None, exif_data)
    new_fn = filemap.new_fn
    assert old_fn == new_fn


def test_get_new_fn_with_no_exif_data():
    """Test get_new_fn() with no EXIF data and old_fn with correct file
    extension."""
    exif_data = {}
    old_fn = 'abc123.jpg'
    filemap = FileMap(old_fn, None, exif_data)
    new_fn = filemap.new_fn
    assert old_fn == new_fn


def test_get_new_fn_with_exif_data_and_wrong_ext():
    """Test get_new_fn() with valid EXIF data and wrong file extension."""
    exif_data = {'DateTimeOriginal': '2014:08:16 06:20:20'}
    old_fn = 'abc123.jpeg'
    filemap = FileMap(old_fn, None, exif_data)
    new_fn = filemap.new_fn
    assert new_fn == '20140816_062020.jpg'


@patch('jpeg_rename.TAGS')
@patch.object(Image, 'open')
def test_get_exif_data(mock_img, mock_tags):
    """
    """
    class TestImage():
        def _getexif(self):
            return {'DateTimeOriginal': '2014:08:16 06:20:20'}

    def get(arg1, arg2):
        return 'DateTimeOriginal'

    old_fn = 'abc123.jpg'
    mock_img.return_value = TestImage()
    mock_tags.get = get
    filemap = FileMap(old_fn)
    assert filemap.exif_data == {'DateTimeOriginal': '2014:08:16 06:20:20'}


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

@patch('jpeg_rename.FileMap.make_new_fn_unique')
@patch('jpeg_rename.os.rename')
def test_move_orthodox(mock_os, mock_fn_unique):
    """Rename file with mocked os.rename. Verify called with args."""
    mock_fn_unique.return_value = None
    old_fn = 'abc123.jpg'
    exif_data = {'DateTimeOriginal': '2014:08:16 06:20'}
    filemap = FileMap(old_fn, avoid_collisions=None, exif_data=exif_data)
    new_fn = filemap.new_fn
    filemap.move()
    mock_os.assert_called_with(old_fn, new_fn)

@patch('jpeg_rename.FileMap.make_new_fn_unique')
@patch('jpeg_rename.os.rename')
def test_move_orthodox_rename_raises_exeption(mock_os, mock_fn_unique):
    """Rename file with mocked os.rename. Verify called with args."""
    mock_fn_unique.return_value = None
    mock_os.side_effect = OSError((1, "Just testing.",))
    old_fn = 'abc123.jpg'
    exif_data = {'DateTimeOriginal': '2014:08:16 06:20'}
    filemap = FileMap(old_fn, avoid_collisions=None, exif_data=exif_data)
    new_fn = filemap.new_fn
    filemap.move()
    mock_os.assert_called_with(old_fn, new_fn)

@patch('jpeg_rename.FileMap.make_new_fn_unique')
@patch('jpeg_rename.os.rename')
def test_move_orthodox_fn_unique_raises_exception(mock_os, mock_fn_unique):
    """Rename file with mocked os.rename. Verify called with args."""
    mock_fn_unique.side_effect = OSError((1, "Just testing.",))
    old_fn = 'abc123.jpg'
    exif_data = {'DateTimeOriginal': '2014:08:16 06:20'}
    filemap = FileMap(old_fn, avoid_collisions=None, exif_data=exif_data)
    new_fn = filemap.new_fn
    with pytest.raises(OSError):
        filemap.move()

@patch('jpeg_rename.FileMap.make_new_fn_unique')
@patch('jpeg_rename.os.path.exists')
def test_move_collision_detected(mock_exists, mock_fn_unique):
    """Move file with collision_detected simulating avoid_collisions = False.
    """
    mock_fn_unique.return_value = None
    mock_exists.return_value = True
    old_fn = 'abc123.jpg'
    exif_data = {}
    filemap = FileMap(old_fn, avoid_collisions=None, exif_data=exif_data)
    filemap.collision_detected = True
    new_fn = filemap.new_fn
    filemap.move()
    assert new_fn == old_fn

@patch('jpeg_rename.os.path.exists')
def test_rename_empty_exif_data(mock_exists):
    """Make unique filename with empty EXIF data."""
    mock_exists.return_value = True
    old_fn = 'abc123.jpg'
    exif_data = {'DateTimeOriginal': '2014:08:16 06:20'}
    filemap = FileMap(old_fn, avoid_collisions=True, exif_data=exif_data)
    new_fn = filemap.new_fn
    filemap.make_new_fn_unique()
    assert filemap.new_fn == old_fn

@patch('jpeg_rename.os.path.exists')
def test_rename_with_valid_exif_data_and_avoid_collisions(mock_exists):
    """Make unique new filename from valid EXIF data. Avoid collisions."""
    mock_exists.return_value = True
    old_fn = 'abc123.jpg'
    exif_data = {'DateTimeOriginal': '2014:08:16 06:20:20'}
    filemap = FileMap(old_fn, avoid_collisions=True, exif_data=exif_data)
    new_fn = filemap.new_fn
    filemap.MAX_RENAME_ATTEMPTS = 2
    with pytest.raises(Exception):
        filemap.make_new_fn_unique()
    assert filemap.new_fn == '20140816_062020.jpg'

@patch('jpeg_rename.os.path.exists')
def test_rename_with_valid_exif_data_and_no_avoid_collisions(mock_exists):
    """Make unique new filename from valid EXIF data. Do not avoid collisions.
    """
    mock_exists.return_value = True
    old_fn = 'abc123.jpg'
    exif_data = {'DateTimeOriginal': '2014:08:16 06:20:20'}
    filemap = FileMap(old_fn, avoid_collisions=False, exif_data=exif_data)
    new_fn = filemap.new_fn
    filemap.MAX_RENAME_ATTEMPTS = 2
    filemap.make_new_fn_unique()
    assert filemap.new_fn == '20140816_062020.jpg'

@patch('jpeg_rename.os.path.exists')
def test_rename_no_collision(mock_exists):
    """Make unique new filename from valid EXIF data. Do not avoid collisions.
    """
    mock_exists.return_value = False
    old_fn = 'abc123.jpg'
    exif_data = {}
    filemap = FileMap(old_fn, avoid_collisions=False, exif_data=exif_data)
    new_fn = filemap.new_fn
    filemap.make_new_fn_unique()
    assert filemap.new_fn == old_fn

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.FileMap')
@patch('jpeg_rename.glob')
def test_init_file_map_orthodox(mock_glob, mock_filemap):
    """
    """
    mock_filemap.return_value = True
    mock_glob.glob.return_value = ['/foo/bar']
    file_map = init_file_map('.')
    assert file_map == [True, True, True]

#@pytest.mark.skipif('True', reason="Work in progress")
@patch('jpeg_rename.FileMap')
@patch('jpeg_rename.glob')
def test_init_file_map_raises_exception(mock_glob, mock_filemap):
    """
    """
    mock_filemap.side_effect = Exception("Just testing.")
    mock_glob.glob.return_value = ['/foo/bar']
    with pytest.raises(Exception):
        file_map = init_file_map('.')

class TestFileMap():

    def __init__(self):
        self.old_fn = 'foo.jpg'
        self.new_fn = 'bar.jpg'

