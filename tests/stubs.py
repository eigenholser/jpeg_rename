"""
Stubs shared between different test modules.
"""
import re
import pytest
from photo_rename import Harvester

# Setup valid EXIF data with expected new filename
EXIF_DATA_VALID = {
    'exif_data': {
        'Exif.Image.DateTime': '2014:08:26 06:20:20'
    },
}
EXIF_DATA_NOT_VALID = {'Exif.Image.DateTime': '2014:08:26 06:20'}
expected_new_fn = re.sub(r':', r'',
        EXIF_DATA_VALID['exif_data']['Exif.Image.DateTime'])
expected_new_fn = re.sub(r' ', r'_', expected_new_fn)
expected_new_fn = '{0}.jpg'.format(expected_new_fn)
EXIF_DATA_VALID['expected_new_fn'] = expected_new_fn
OLD_FN_JPG_LOWER = 'filename.jpg'
OLD_FN_JPG_UPPER = 'filename.JPG'
OLD_FN_JPEG = 'filename.jpg'
IMAGE_TYPE_ARW = 1
IMAGE_TYPE_JPEG = 2
IMAGE_TYPE_PNG = 3
IMAGE_TYPE_TIFF = 4
SKIP_TEST = True
RUN_TEST = False


class StubFileMap(object):
    """
    Stub to be used in place of FileMap().
    """

    def __init__(self):
        self.old_fn = 'foo.jpg'
        self.new_fn = 'bar.jpg'

@pytest.fixture
def harvey():
    return Harvester()
