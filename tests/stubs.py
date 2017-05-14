"""
Stubs shared between different test modules.
"""
import os
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
expected_dst_fn = re.sub(r':', r'',
        EXIF_DATA_VALID['exif_data']['Exif.Image.DateTime'])
expected_dst_fn = re.sub(r' ', r'_', expected_dst_fn)
expected_dst_fn = '{0}.jpg'.format(expected_dst_fn)
EXIF_DATA_VALID['expected_dst_fn'] = expected_dst_fn
SRC_FN_JPG_LOWER = 'filename.jpg'
SRC_FN_JPG_UPPER = 'filename.JPG'
SRC_FN_JPEG = 'filename.jpg'
IMAGE_TYPE_ARW = 1
IMAGE_TYPE_JPEG = 2
IMAGE_TYPE_PNG = 3
IMAGE_TYPE_TIFF = 4
SKIP_TEST = True
RUN_TEST = False


class StubFilemap(object):
    """
    Stub to be used in place of Filemap().
    """

    def __init__(self):
        self.src_fn = 'foo.jpg'
        self.dst_fn = 'bar.jpg'

    def set_dst_fn(self, dst_fn_fq):
        self.dst_fn_fq = dst_fn_fq
        self.dst_fn = os.path.basename(dst_fn_fq)


@pytest.fixture
def harvey():
    return Harvester('.')

