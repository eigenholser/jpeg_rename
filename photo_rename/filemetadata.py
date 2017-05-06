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
        self.metadata = self.read_metadata(file)

    def read_metadata(self, file):
        """
        Read EXIF or XMP data from file. Convert to Python dict.
        """
        # Xmp.xmp.CreateDate
        # Exif.Image.DateTime
        img_md = pyexiv2.ImageMetadata("{}".format(file))
        img_md.read()

        metadata = {}

        import pdb; pdb.set_trace()
        xmp_keys = [md_key for md_key in img_md.xmp_keys]
        exif_keys = [md_key for md_key in img_md.exif_keys]

        for key in xmp_keys + exif_keys:
            tag = img_md[key].raw_value
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

        img_md = pyexiv2.ImageMetadata("{}".format(self.file))
        img_md.read()

        if 'Xmp.xmp.MetadataDate' in self.metadata:
            pass
        if 'Xmp.xmp.CreateDate' in self.metadata:
            pass
        if 'Exif.Image.DateTime' in self.metadata:
            img_md['Exif.Image.DateTime'] = pyexiv2.ExifTag(
                    'Exif.Image.DateTime', exif_datetime)
        if 'Exif.Photo.DateTimeOriginal' in self.metadata:
            img_md['Exif.Photo.DateTimeOriginal'] = pyexiv2.ExifTag(
                    'Exif.Photo.DateTimeOriginal', exif_datetime)

        try:
            img_md.write()
        except Exception as e:
            logger.error(e)

