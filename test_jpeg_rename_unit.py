
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
    filemap = FileMap(old_fn, exif_data)
    new_fn = filemap.new_fn
    assert old_fn == new_fn


def test_get_new_fn_with_no_exif_data():
    """Test get_new_fn() with no EXIF data and old_fn with correct file
    extension."""
    exif_data = {}
    old_fn = 'abc123.jpg'
    filemap = FileMap(old_fn, exif_data)
    new_fn = filemap.new_fn
    assert old_fn == new_fn


def test_get_new_fn_with_exif_data_and_wrong_ext():
    """Test get_new_fn() with valid EXIF data and wrong file extension."""
    exif_data = {'DateTimeOriginal': '2014:08:16 06:20:20'}
    old_fn = 'abc123.jpeg'
    filemap = FileMap(old_fn, exif_data)
    new_fn = filemap.new_fn
    assert new_fn == '20140816_062020.jpg'


class TestFileMap():

    def __init__(self):
        self.old_fn = 'foo.jpg'
        self.new_fn = 'bar.jpg'

