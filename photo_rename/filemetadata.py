import argparse
from datetime import datetime
import logging
import os
import re
import stat
import sys
import pyexiv2
import photo_rename


logger = logging.getLogger(__name__)


@photo_rename.logged_class
class FileMetadata(object):
    """
    Contains logic to perform metadata operations on file.
    """

    def __init__(self, file):
        self.file = file
        self.metadata = None
        self.img_md = pyexiv2.ImageMetadata("{}".format(file))
        self.img_md.read()

    def __getitem__(self, key):
        """
        Magic method for getting data.
        """
        if key == "metadata":
            if not self.metadata:
                self.metadata = self.read_metadata(self.file)
            return self.metadata

    def read_metadata(self, file):
        """
        Read EXIF or XMP data from file. Convert to Python dict.
        """
        metadata = {}

        xmp_keys = [md_key for md_key in self.img_md.xmp_keys]
        exif_keys = [md_key for md_key in self.img_md.exif_keys]

        for key in xmp_keys + exif_keys:
            tag = self.img_md[key].raw_value
            metadata[key] = tag

        return metadata

    def set_datetime(self, new_datetime):
        """
        Update EXIF/XMP tags as needed and write metadata.
        """
        # TODO: Timezone?
        xmp_datetime = new_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        exif_datetime = new_datetime.strftime('%Y:%m:%d %H:%M:%S')
        logger.debug("XMP: {} : EXIF: {}".format(xmp_datetime, exif_datetime))

        # Shotwell will use Xmp.xmp.CreateDate if set, so it must be updated.
        if 'Xmp.xmp.CreateDate' in self['metadata'].keys():
            self.img_md['Xmp.xmp.CreateDate'] = pyexiv2.XmpTag(
                    'Xmp.xmp.CreateDate', new_datetime)
        if 'Exif.Photo.DateTimeOriginal' in self['metadata'].keys():
            self.img_md['Exif.Photo.DateTimeOriginal'] = pyexiv2.ExifTag(
                    'Exif.Photo.DateTimeOriginal', new_datetime)
        self.img_md['Exif.Image.DateTime'] = pyexiv2.ExifTag(
                'Exif.Image.DateTime', new_datetime)

        try:
            self.img_md.write()
        except Exception as e:
            logger.error(e)

    def copy_metadata(self, tgt_fn):
        """
        Copy metadata from self.file to tgt_fn.
        """
        tgt_md = pyexiv2.ImageMetadata("{}".format(tgt_fn))
        tgt_md.read()

        self.img_md.copy(tgt_md, exif=True, iptc=True, xmp=True, comment=True)

        try:
            tgt_md.write()
        except Exception as e:
            logger.error(e)



