#!/usr/bin/env python

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
        'abc123.jpg'
        >>>
        """
        self.logger.debug("Old filename: {}".format(old_fn))
        self.MAX_RENAME_ATTEMPTS = MAX_RENAME_ATTEMPTS
        self.old_fn_fq = old_fn
        self.workdir = os.path.dirname(old_fn)
        self.old_fn = os.path.basename(old_fn)
        self.image_type = image_type
        self.metadata = metadata

        self.old_fn_base = self.get_base(self.old_fn)
        self.old_fn_base_lower = self.get_base(self.old_fn).lower()
        self.old_fn_ext = self.get_extension(self.old_fn)
        self.old_fn_ext_lower = self.get_extension(self.old_fn).lower()

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

    def get_base(self, filename):
        """
        Return the filename base--i.e. without extension.
        """
        res = re.search(r"^(.+)\..+$", filename)
        if res:
            return res.group(1)
        return None

    def get_extension(self, filename):
        """
        Return the file extension of the old filename.
        """
        res = re.search(r"^.+\.(.+)$", filename)
        if res:
            return res.group(1)
        return None

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


@logged_class
class FileMapList(object):
    """
    Intelligently add FileMap() instances to file_map list based on order of
    instance.new_fn attributes.
    """

    def __init__(self):
        self.file_map = []

    def add(self, instance):
        """
        Add, whether insert or append, a FileMap instance to the file_map list
        in the order of instance.new_fn. If there are duplicate new_fn in the
        list, they will be resolved in instance.move().
        """
        index = 0
        inserted = False
        for fm in self.file_map:
            if instance.new_fn < fm.new_fn:
                self.file_map.insert(index, instance)
                inserted = True
                break
            index += 1

        # Reached end of list with no insert. Append to list instead.
        if not inserted:
            self.file_map.append(instance)

    def get(self):
        """
        Define a generator function here to return items on the file_map
        list.
        """
        return (x for x in self.file_map)


def init_file_map(workdir, mapfile=None, avoid_collisions=None):
    """
    Read the work directory looking for files with extensions defined in the
    EXTENSIONS constant. Note that this could use a more elaborate magic
    number mechanism that would be cool.
    """

    # List of FileMap objects.
    file_map_list = FileMapList()

    list_workdir = os.listdir(workdir)
    if mapfile:
        # Extract files in work dir that match against our alternate file map.
        #
        # alt_file_map.keys() = ['abc', 'def', 'ghi', 'jkl', 'mno']
        # list_workdir = ['abc.jpg', 'ghi.jpg', 'pqr.jpg']
        # results in...
        # all_files_list = ['abc.jpg', 'ghi.jpg']

        alt_file_map = read_alt_file_map(mapfile)
        all_files_list = []
        filename_prefix_map = {}
        for file_prefix in alt_file_map.keys():
            for filename in list_workdir:
                if re.search(r"^{}\..+$".format(file_prefix), filename):
                    all_files_list.append(filename)
                    filename_prefix_map[filename] = file_prefix
    else:
        all_files_list = list_workdir

    # Initialize file_map list.
    for extension in EXTENSIONS:
        image_regex = r"\." + re.escape(extension) + r"$"
        matching_files = [filename for filename in all_files_list
                if re.search(image_regex, filename, re.IGNORECASE)]
        logger.debug(matching_files)
        for filename in (matching_files):
            filename_fq = os.path.join(workdir, filename)
            # TODO: There once was some trouble here that caused me to comment
            # the directory check. Dunno. Keep an eye on it in case it pops up
            # again in the future.
            if os.path.isdir(filename_fq):
                logger.warn("Skipping directory {0}".format(filename_fq))
                continue
            try:
                image_type = EXTENSION_TO_IMAGE_TYPE[extension]
                if mapfile:
                    filename_prefix = filename_prefix_map[filename]
                    new_fn = "{}.{}".format(
                            alt_file_map[filename_prefix], extension)
                    file_map_list.add(
                        FileMap(filename_fq, image_type, avoid_collisions, {},
                            new_fn))
                else:
                    file_map_list.add(FileMap(
                        filename_fq, image_type, avoid_collisions))
            except Exception as e:
                logger.warn("FileMap Error: {0}".format(e))
    return file_map_list


def read_alt_file_map(mapfile, delimiter='\t'):
    """
    Read a filename map for the purpose of transforming the filenames as an
    alternative to using EXIF/XMP metadata DateTime information. Only require
    map file as an absolute path.
    """
    with open(mapfile, 'r') as f:
        lines = f.readlines()

    # XXX: This is soooo cool! List of lists flattened all on one nested
    # comprehension.
    # [[k1, v1], [k2, v2], ..., [kn, vn]] --> {k1: v1, k2: v2, ..., kn: vn}
    return dict(zip(*[iter([x for sublist in [
        str.split(line.rstrip('\n'), delimiter) for line in lines]
        for x in sublist])] * 2))


def process_file_map(file_map, simon_sez=None, move_func=None):
    """
    Iterate through the Python list of FileMap objects. Move the file if
    Simon sez.

    Arguments:
        str: workdir - Working directory.
        dict: file_map - old_fn to new_fn mapping.
        boolean: simon_sez - Dry run or real thing.
        func: move_func - Move function to use for testing or default.
    Returns:
        None

    >>> filemap = FileMap('IMG0332.JPG', 'jpg', avoid_collisions=None, metadata={'Exif.Image.DateTime': '2014-08-18 20:23:83'})
    >>> def move_func(old_fn, new_fn): pass
    >>> file_map_list = FileMapList()
    >>> file_map_list.add(filemap)
    >>> process_file_map(file_map_list, True, move_func)

    """

    # XXX: Of marginal utility
    if simon_sez is None:
        simon_sez = False

    fm_list = file_map.get()
    for fm in fm_list:
        try:
            if simon_sez:
                if move_func is None:
                    fm.move()
                else:
                    move_func(fm.old_fn, fm.new_fn)
            else:
                if fm.old_fn != fm.new_fn:
                    logging.info("DRY RUN: Moving {0} ==> {1}".format(
                        fm.old_fn, fm.new_fn))
                    fm.same_files = False   # For unit test only.
        except Exception as e:
            logging.info("{0}".format(e))
            break


def process_all_files(
        workdir=None, simon_sez=None, avoid_collisions=None, mapfile=None):
    """
    Manage the entire process of gathering data and renaming files.
    """
    if not os.path.exists(workdir):
        logging.error(
                "Directory {0} does not exist. Exiting.".format(workdir))
        sys.exit(1)

    if not os.access(workdir, os.W_OK):
        logging.error(
                "Directory {0} is not writable. Exiting.".format(workdir))
        sys.exit(1)

    #import pdb; pdb.set_trace()
    file_map = init_file_map(workdir, mapfile, avoid_collisions)
    process_file_map(file_map, simon_sez)


def main():
    """
    Parse command-line arguments. Initiate file processing.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--simon-sez",
            help="Really, Simon sez rename the files!", action="store_true")
    parser.add_argument("-a", "--avoid-collisions",
            help="Append suffix until filenames do not collide. 10x max.",
            action="store_true")
    parser.add_argument("-d", "--directory",
            help="Read files from this directory.")
    parser.add_argument("-m", "--mapfile",
            help="Use this map to rename files. Do not use metadata.")
    parser.add_argument("-v", "--verbose", help="Log level to DEBUG.",
            action="store_true")
    myargs = parser.parse_args()

    # Use current directory if --directory not specified.
    workdir = myargs.directory
    if workdir is None:
        workdir = os.path.dirname(os.path.abspath(__file__))

    # Validate --map
    mapfile = myargs.mapfile
    if mapfile:
        # --map is not compatible with --avoid-collisions.
        error = False
        if myargs.directory:
            logging.error("May not specify --directory with --mapfile.")
            error = True
        else:
            workdir = os.path.dirname(os.path.abspath(mapfile))
        if myargs.avoid_collisions:
            logging.error(
                    "May not specify --avoid-collisions with --mapfile.")
            error = True
        if not os.path.exists(mapfile):
            logging.error("Map file {} does not exist.".format(mapfile))
            error = True
        if not os.access(mapfile, os.R_OK):
            logging.error("Map file {} is not readable.".format(mapfile))
            error = True
        if error:
            logging.error("Exiting due to errors.")
            sys.exit(1)

    if (myargs.verbose):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    process_all_files(workdir=workdir, simon_sez=myargs.simon_sez,
            avoid_collisions=myargs.avoid_collisions, mapfile=mapfile)

if __name__ == '__main__':  # pragma: no cover
    main()
