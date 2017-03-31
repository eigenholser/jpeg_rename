import argparse
import logging
import os
import re
import stat
import sys
import pyexiv2


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
logger = logging.getLogger(__name__)


def logged_class(cls):
    """
    Class Decorator to add a class level logger to the class with module and
    name.
    """
    cls.logger = logging.getLogger(
            "{0}.{1}".format(cls.__module__, cls.__name__))
    return cls


@logged_class
class FileMap(object):
    """
    FileMap represents a mapping between the old_fn and the new_fn. It's
    methods perform all necessary instance functions for the rename.
    """

    def __init__(self, old_fn, image_type, avoid_collisions=None,
            metadata=None, new_fn=None):
        """
        Initialize FileMap instance.

        >>> filemap = FileMap('abc123.jpeg', IMAGE_TYPE_JPEG, None, {})
        >>> filemap.old_fn
        'abc123.jpeg'
        >>> filemap.new_fn
        'abc123.jpeg'
        >>>
        """
        self.logger.debug("Old filename: {}".format(old_fn))
        self.MAX_RENAME_ATTEMPTS = MAX_RENAME_ATTEMPTS
        self.old_fn_fq = old_fn
        self.workdir = os.path.dirname(old_fn)
        self.old_fn = os.path.basename(old_fn)
        self.image_type = image_type
        self.metadata = metadata

        self.old_fn_base = os.path.splitext(self.old_fn)[0]
        self.old_fn_base_lower = os.path.splitext(self.old_fn)[0].lower()
        self.old_fn_ext = os.path.splitext(self.old_fn)[1][1:]
        self.old_fn_ext_lower = os.path.splitext(self.old_fn)[1][1:].lower()

        # Avoid filename collisions (dangerous) or log a message if there
        # would be one, and fail the move. When set to False, rename attempt
        # will be aborted for safety.
        self.collision_detected = False
        if avoid_collisions is None:
            self.avoid_collisions = False
        else:
            self.avoid_collisions = avoid_collisions

        if not new_fn:
            # Read EXIF or XMP metadata from old filename
            if metadata is None:
                self.metadata = self.read_metadata()
            else:
                self.metadata = metadata
            new_fn = self.build_new_fn()

        self.logger.debug("Using new_fn: {}".format(new_fn))
        self.new_fn = new_fn
        self.new_fn_fq = os.path.join(self.workdir, new_fn)
        self.logger.debug(
                "Initializing file mapper object for filename {}".format(
                    self.new_fn))

    def read_metadata(self):
        """
        Read EXIF or XMP data from file. Convert to Python dict.
        """
        # Xmp.xmp.CreateDate
        # XXX: We already know file exists 'cuz we found it.
        img_md = pyexiv2.ImageMetadata("{}".format(self.old_fn_fq))
        img_md.read()

        metadata = {}

        if (self.image_type == IMAGE_TYPE_PNG):
            metadata_keys = [md_key for md_key in img_md.xmp_keys]
        else:
            metadata_keys = [md_key for md_key in img_md.exif_keys]

        for exifkey in metadata_keys:
            tag = img_md[exifkey].raw_value
            self.logger.debug(exifkey)
            self.logger.debug("{}: {}".format(exifkey, tag))
            metadata[exifkey] = tag

        if (len(metadata) == 0):
            raise Exception("{0} has no EXIF data.".format(self.old_fn))

        return metadata

    def build_new_fn(self):
        """
        Generate new filename from old_fn EXIF or XMP data if possible. Even if
        not possible, lowercase old_fn and normalize file extension.

        >>> filemap = FileMap('abc123.jpeg', IMAGE_TYPE_JPEG, avoid_collisions=None, metadata={'Exif.Image.DateTime': '2014:08:16 06:20:30'})
        >>> filemap.new_fn
        '20140816_062030.jpg'

        """

        # Start with EXIF DateTime
        try:
            if (self.image_type == IMAGE_TYPE_PNG):
                new_fn = self.metadata['Xmp.xmp.CreateDate']
            else:
                new_fn = self.metadata['Exif.Image.DateTime']
        except KeyError:
            new_fn = None

        # If this pattern does not strictly match then keep original name.
        # YYYY:MM:DD HH:MM:SS (EXIF) or YYYY-MM-DDTHH:MM:SS (XMP)
        if (new_fn and not
                re.match(r'^\d{4}\W\d\d\W\d\d.\d\d\W\d\d\W\d\d$', new_fn)):
            # Setup for next step.
            new_fn = None

        # Don't assume exif tag exists. If it does not, keep original filename.
        # Lowercase extension.
        if new_fn is None:
            new_fn = "{base}.{ext}".format(
                    base=self.old_fn_base, ext=self.old_fn_ext_lower)
        else:
            new_fn = "{0}.{1}".format(
                    new_fn, EXTENSIONS_PREFERRED[self.image_type])

        # XXX: One may argue that the next step should be an 'else' clause of
        # the previous 'if' statement. But the intention here is to clean up
        # just a bit even if we're not really renaming the file. Windows
        # doesn't like colons in filenames.

        # Rename using Exif.Image.DateTime or Xmp.xmp.CreateDate
        new_fn = re.sub(r':', r'', new_fn)
        new_fn = re.sub(r'-', r'', new_fn)
        new_fn = re.sub(r' ', r'_', new_fn)
        new_fn = re.sub(r'T', r'_', new_fn)

        return new_fn

    def _chmod(self):
        """
        Removes execute bit from file permission for USR, GRP, and OTH.
        """
        st = os.stat(self.new_fn_fq)
        self.logger.info(
                "Removing execute permissions on {0}.".format(self.new_fn))
        if bool(st.st_mode & stat.S_IXUSR):
            os.chmod(self.new_fn_fq, st.st_mode ^ stat.S_IXUSR)
        if bool(st.st_mode & stat.S_IXGRP):
            os.chmod(self.new_fn_fq, st.st_mode ^ stat.S_IXGRP)
        if bool(st.st_mode & stat.S_IXOTH):
            os.chmod(self.new_fn_fq, st.st_mode ^ stat.S_IXOTH)

    def move(self):
        """
        Move old_fn to new_fn.
        """
        # XXX: This call deliberately placed here instead of __init__(). All
        # initialization is performed before any files are moved. The file
        # move will change state and may introduce a collision. Doing the
        # uniqueness check here will check current state.
        try:
            self.make_new_fn_unique()
        except Exception as e:
            raise e

        if self.collision_detected:
            self.logger.warn(
                "{0} => {1} Destination collision. Aborting.".format(
                self.old_fn, self.new_fn))
                #os.path.basename(self.old_fn), os.path.basename(self.new_fn)))
            return

        try:
            # XXX: Unit tests did not catch this bug.
            # os.rename(self.old_fn, self.new_fn)
            if self.old_fn != self.new_fn:
                self.logger.info("Moving the files: {0} ==> {1}".format(
                    self.old_fn, self.new_fn))
                os.rename(self.old_fn_fq, self.new_fn_fq)
            self._chmod()
        except OSError as e:
            self.logger.warn("Unable to rename file: {0}".format(e.strerror))

    def make_new_fn_unique(self):
        """
        Check new_fn for uniqueness in 'workdir'. Rename, adding a numerical
        suffix until it is unique. Impose limits to avoid long loop.
        """
        # Rename file by appending number if we have collision.
        # TODO: I wish I didn't specify \d+_\d+ for the first part. perhaps
        # not -\d\ before .jpg would be better for the second match.
        counter = 1
        while(os.path.exists(self.new_fn_fq)):
            if (self.old_fn == self.new_fn):
                # Same file, faux collision.
                break
            if (not self.avoid_collisions):
                # Abort - do not attempt to rename.
                # If we're using a map file, this will prevent clobbering a
                # previous file if in error a duplicate new_fn is in the map.
                self.collision_detected = True
                break

            # Since we're renaming files that may have already been renamed
            # with a `-#' suffix, we need to catch that pattern first.
            new_fn_regex_s1 = r"^(\d+_\d+)-\d+\.{}".format(
                    EXTENSIONS_PREFERRED[self.image_type])
            new_fn_regex_s2 = r"^(\d+_\d+)\.{}".format(
                    EXTENSIONS_PREFERRED[self.image_type])
            new_fn_regex_r = r"\1-{0}.{1}".format(counter,
                    EXTENSIONS_PREFERRED[self.image_type])
            new_fn = re.sub(new_fn_regex_s1, new_fn_regex_r, self.new_fn)
            new_fn = re.sub(new_fn_regex_s2, new_fn_regex_r, new_fn)

            self.new_fn = new_fn
            self.new_fn_fq = os.path.join(self.workdir, new_fn)

            counter += 1
            if counter > self.MAX_RENAME_ATTEMPTS:
                raise Exception(
                    "Too many rename attempts: {0}".format(self.new_fn))
