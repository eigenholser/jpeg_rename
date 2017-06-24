import argparse
import logging
import os
import re
import stat
import sys
import pyexiv2
import photo_rename


logger = logging.getLogger(__name__)


@photo_rename.logged_class
class Filemap(object):
    """
    Filemap represents a mapping between the src_fn and the dst_fn. It's
    methods perform all necessary instance functions for the rename.
    """

    def __init__(self, src_fn, image_type, metadata=None, dst_fn=None,
            read_metadata=True):
        """
        Initialize Filemap instance.

        >>> filemap = Filemap('abc123.jpeg', photo_rename.IMAGE_TYPE_JPEG, None, {})
        >>> filemap.src_fn
        'abc123.jpeg'
        >>> filemap.dst_fn
        'abc123.jpeg'
        >>>
        """
        self.logger.debug("Old filename: {}".format(src_fn))
        self.MAX_RENAME_ATTEMPTS = photo_rename.MAX_RENAME_ATTEMPTS
        self.src_fn_fq = src_fn
        self.workdir = os.path.dirname(src_fn)
        self.src_fn = os.path.basename(src_fn)
        self.image_type = image_type
        self.metadata = metadata

        self.src_fn_base = os.path.splitext(self.src_fn)[0]
        self.src_fn_base_lower = os.path.splitext(self.src_fn)[0].lower()
        self.src_fn_ext = os.path.splitext(self.src_fn)[1][1:]
        self.src_fn_ext_lower = os.path.splitext(self.src_fn)[1][1:].lower()

        # TODO: Deprecated...
        # Avoid filename collisions (dangerous) or log a message if there
        # would be one, and fail the move. When set to False, rename attempt
        # will be aborted for safety.
        self.collision_detected = False

        # Read EXIF or XMP metadata from old filename
        if metadata is None and read_metadata:
            self.metadata = self.read_metadata()
        else:
            self.metadata = metadata

        if not dst_fn:
            # This may be temporary. When the collision check is done it may
            # change.
            dst_fn = self.build_dst_fn()

        self.logger.debug("Using dst_fn: {}".format(dst_fn))
        self.set_dst_fn(os.path.join(self.workdir, dst_fn))
        self.logger.debug(
                "Initializing file mapper object for filename {}".format(
                    self.dst_fn))

    def set_dst_fn(self, dst_fn_fq):
        """
        Setter for dst_fn.
        """
        self.dst_fn_fq = dst_fn_fq
        self.dst_fn = os.path.basename(dst_fn_fq)

    def read_metadata(self):
        """
        Read EXIF or XMP data from file. Convert to Python dict.
        """
        # Xmp.xmp.CreateDate
        # XXX: We already know file exists 'cuz we found it.
        img_md = pyexiv2.ImageMetadata("{}".format(self.src_fn_fq))
        img_md.read()

        metadata = {}

        if (self.image_type == photo_rename.IMAGE_TYPE_PNG):
            metadata_keys = [md_key for md_key in img_md.xmp_keys]
        else:
            metadata_keys = [md_key for md_key in img_md.exif_keys]

        for exifkey in metadata_keys:
            tag = img_md[exifkey].raw_value
            #self.logger.debug(exifkey)
            #self.logger.debug("{}: {}".format(exifkey, tag))
            metadata[exifkey] = tag

        if (len(metadata) == 0):
            raise Exception("{0} has no EXIF data.".format(self.src_fn))

        return metadata

    def build_dst_fn(self):
        """
        Generate dst filename from src_fn EXIF or XMP data if possible. Even if
        not possible, lowercase src_fn and normalize file extension.

        >>> filemap = Filemap('abc123.jpeg', photo_rename.IMAGE_TYPE_JPEG, metadata={'Exif.Image.DateTime': '2014:08:16 06:20:30'})
        >>> filemap.dst_fn
        '20140816_062030.jpg'

        """

        # Start with EXIF DateTime
        try:
            if (self.image_type == photo_rename.IMAGE_TYPE_PNG):
                dst_fn = self.metadata['Xmp.xmp.CreateDate']
            else:
                dst_fn = self.metadata['Exif.Image.DateTime']
        except KeyError:
            dst_fn = None

        # If this pattern does not strictly match then keep original name.
        # YYYY:MM:DD HH:MM:SS (EXIF) or YYYY-MM-DDTHH:MM:SS (XMP)
        if (dst_fn and not
                re.match(r'^\d{4}\W\d\d\W\d\d.\d\d\W\d\d\W\d\d$', dst_fn)):
            # Setup for next step.
            dst_fn = None

        # Don't assume exif tag exists. If it does not, keep original filename.
        # Lowercase extension.
        if dst_fn is None:
            dst_fn = "{base}.{ext}".format(
                    base=self.src_fn_base, ext=self.src_fn_ext_lower)
        else:
            dst_fn = "{0}.{1}".format(
                dst_fn, photo_rename.EXTENSIONS_PREFERRED[self.image_type])

        # XXX: One may argue that the next step should be an 'else' clause of
        # the previous 'if' statement. But the intention here is to clean up
        # just a bit even if we're not really renaming the file. Windows
        # doesn't like colons in filenames.

        # Rename using Exif.Image.DateTime or Xmp.xmp.CreateDate
        dst_fn = re.sub(r':', r'', dst_fn)
        dst_fn = re.sub(r'-', r'', dst_fn)
        dst_fn = re.sub(r' ', r'_', dst_fn)
        dst_fn = re.sub(r'T', r'_', dst_fn)

        return dst_fn

    def _chmod(self):
        """
        Removes execute bit from file permission for USR, GRP, and OTH.
        """
        st = os.stat(self.dst_fn_fq)
        self.logger.info(
                "Removing execute permissions on {0}.".format(self.dst_fn))
        mode = st.st_mode
        if bool(st.st_mode & stat.S_IXUSR):
            mode = mode ^ stat.S_IXUSR
            os.chmod(self.dst_fn_fq, mode)
        if bool(st.st_mode & stat.S_IXGRP):
            mode = mode ^ stat.S_IXGRP
            os.chmod(self.dst_fn_fq, mode)
        if bool(st.st_mode & stat.S_IXOTH):
            mode = mode ^ stat.S_IXOTH
            os.chmod(self.dst_fn_fq, mode)

    def move(self):
        """
        Move src_fn to dst_fn.
        """
        if self.src_fn == self.dst_fn:
            self.logger.debug("Not moving {} ==> {}. No change.".format(
                self.src_fn, self.dst_fn))
            return

        if os.path.exists(self.dst_fn_fq):
            self.collision_detected = True
            self.logger.warn(
                "{0} => {1} Destination collision. Doing nothing.".format(
                self.src_fn, self.dst_fn))
            return

        try:
            # XXX: Unit tests did not catch this bug.
            # os.rename(self.src_fn, self.dst_fn)
            if self.src_fn != self.dst_fn:
                self.logger.info("Moving file: {0} ==> {1}".format(
                    self.src_fn, self.dst_fn))
                os.rename(self.src_fn_fq, self.dst_fn_fq)
            self._chmod()
        except OSError as e:
            self.logger.warn("Unable to rename file: {0}".format(e.strerror))

