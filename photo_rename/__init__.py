from .utils import logged_class
from .filemap import FileMap
from .filemaplist import FileList, FileMapList
from .harvester import Harvester

__version__ = "0.5"

# Configure built-in support for various image types.
IMAGE_TYPE_ARW = 1
IMAGE_TYPE_JPEG = 2
IMAGE_TYPE_PNG = 3
IMAGE_TYPE_TIFF = 4
IMAGE_TYPES = {
    IMAGE_TYPE_ARW  : ['arw'],
    IMAGE_TYPE_JPEG : ['jpg', 'jpeg'],
    IMAGE_TYPE_PNG  : ['png'],
    IMAGE_TYPE_TIFF : ['tif', 'tiff'],
}
EXTENSIONS_PREFERRED = {
    IMAGE_TYPE_ARW  : 'arw',
    IMAGE_TYPE_JPEG : 'jpg',
    IMAGE_TYPE_PNG  : 'png',
    IMAGE_TYPE_TIFF : 'tif',
}
EXTENSIONS = [
    ext for sublist in [v for k, v in IMAGE_TYPES.items()] for ext in sublist]
EXTENSION_TO_IMAGE_TYPE = dict([
    (ext, it) for it, sublist in [(k, v) for k, v in IMAGE_TYPES.items()]
    for ext in sublist])
MAX_RENAME_ATTEMPTS = 10
