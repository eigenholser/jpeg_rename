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
    """

    def __init__(self, file):
        """
        Object that reads, writes, and stores EXIF and XMP metadata from file.
        """
        self.file = file
        self.img_md = pyexiv2.ImageMetadata("{}".format(file))
        self.img_md.read()
        self.metadata = self.read_metadata(file)

    def read_metadata(self, file):
        """
        Read EXIF or XMP data from file. Convert to Python dict.
        """
        # Xmp.xmp.CreateDate
        # Exif.Image.DateTime

        metadata = {}

        import pdb; pdb.set_trace()
        xmp_keys = [md_key for md_key in self.img_md.xmp_keys]
        exif_keys = [md_key for md_key in self.img_md.exif_keys]

        for key in xmp_keys + exif_keys:
            tag = self.img_md[key].raw_value
            metadata[key] = tag

        if (len(metadata) == 0):
            raise Exception("{0} has no EXIF/XMP data.".format(self.src_fn))

        return metadata

    def set_datetime(self, new_datetime):
        """
        Update EXIF/XMP tags as needed and write metadata.
        TODO: Test writeable on each file prior to attempt. Not here though.
        TODO: Timezone?
        """
        # Xmp.xmp.MetadataDate : 2017-03-03T08:07:01-07:00
        # Xmp.xmp.CreateDate : 2017-02-27T15:19:31-07:00
        # Exif.Image.DateTime : 2017:03:03 09:27:53
        # Xmp.xmp.ModifyDate : 2017-03-03T09:27:53-07:00
        xmp_datetime = new_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        exif_datetime = new_datetime.strftime('%Y:%m:%d %H:%M:%S')
        logger.debug("XMP: {} : EXIF: {}".format(xmp_datetime, exif_datetime))

        # Shotwell requires Xmp.xmp.CreateDate to be set.
        self.img_md['Xmp.xmp.CreateDate'] = pyexiv2.XmpTag(
                'Xmp.xmp.CreateDate', new_datetime)
        self.img_md['Exif.Image.DateTime'] = pyexiv2.ExifTag(
                'Exif.Image.DateTime', new_datetime)
        self.img_md['Exif.Photo.DateTimeOriginal'] = pyexiv2.ExifTag(
                'Exif.Photo.DateTimeOriginal', new_datetime)

        try:
            self.img_md.write()
        except Exception as e:
            logger.error(e)

