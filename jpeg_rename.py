#!/usr/bin/env python

from __future__ import print_function
import argparse
import glob
import os
import re
import sys
import PIL
from PIL.ExifTags import TAGS
from PIL import Image


# Need to look for *.JPG, *.jpg, and *.jpeg files for consideration.
EXTENSIONS = ['JPG', 'jpg', 'jpeg']
MAX_RENAME_ATTEMPTS = 10


class FileMap():
    """FileMap represents a mapping between the old_fn and the new_fn. It's
    methods perform all necessary instance functions for the rename.

    Arguments:
        str: old_fn - Old Filename
        dict: exif_data - For testing only. Dict with sample EXIF data.
    """

    def __init__(self, old_fn, avoid_collisions=None, exif_data=None):
        """Initialize FileMap instance.

        >>> filemap = FileMap('abc123.jpeg', None, {})
        >>> filemap.old_fn
        'abc123.jpeg'
        >>> filemap.new_fn
        'abc123.jpg'
        >>>
        """
        self.MAX_RENAME_ATTEMPTS = MAX_RENAME_ATTEMPTS
        self.old_fn_fq = old_fn
        self.workdir = os.path.dirname(old_fn)
        self.old_fn = os.path.basename(old_fn)

        # Avoid filename collisions (dangerous) or log a message if there
        # would be one, and fail the move.
        self.collision_detected = False
        if avoid_collisions is None:
            self.avoid_collisions = False
        else:
            self.avoid_collisions = avoid_collisions

        # Read EXIF data from old filename
        if exif_data is None:
            self.read_exif_data()
        else:
            self.exif_data = exif_data

        self.get_new_fn()

    def read_exif_data(self):
        """Read EXIF data from file. Convert to Python dict."""

        # XXX: We already know file exists 'cuz we found it.
        img = Image.open(self.old_fn_fq)
        info = img._getexif()

        self.exif_data ={}
        if info is not None:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                self.exif_data[decoded] = value
        else:
            raise Exception("{0} has no EXIF data.".format(self.old_fn))

    def get_new_fn(self):
        """Generate new filename from old_fn EXIF data if possible. Even if not
        possible, lowercase old_fn and normalize file extension.

        Arguments:
            dict: EXIF data

        >>> filemap = FileMap('abc123.jpeg', avoid_collisions=None, exif_data={'DateTimeOriginal': '2014:08:16 06:20:30'})
        >>> filemap.new_fn
        '20140816_062030.jpg'

        """

        # Start with EXIF DateTimeOriginal
        try:
            new_fn = self.exif_data['DateTimeOriginal']
        except KeyError:
            new_fn = None

        # If this pattern does not strictly match then keep original name.
        # YYYY:MM:DD HH:MM:SS
        if (new_fn and not
                re.match(r'^\d{4}:\d\d:\d\d \d\d:\d\d:\d\d$', new_fn)):
            # Setup for next step.
            new_fn = None

        # Don't assume exif tag exists. If it does not, keep original filename.
        # Lowercase filename base and extension
        if new_fn is None:
            new_fn = self.old_fn.lower()
            new_fn = re.sub(r'.jpeg$', r'.jpg', new_fn)
        else:
            new_fn = "{0}.jpg".format(new_fn)

        # XXX: One may argue that the next step should be an 'else' clause of the
        # previous 'if' statement. But the intention here is to clean up just a bit
        # even if we're not really renaming the file. Windows doesn't like colons
        # in filenames.

        # Rename using exif DateTimeOriginal
        new_fn = re.sub(r':', r'', new_fn)
        new_fn = re.sub(r' ', r'_', new_fn)

        self.new_fn = new_fn
        self.new_fn_fq = os.path.join(self.workdir, new_fn)

    def move(self):
        """Move old_fn to new_fn."""

        # XXX: This call deliberately placed here instead of __init__(). All
        # initialization is performed before any files are moved. The file move
        # will change state and may introduce a collision. Doing the uniqueness
        # check here will check current state.
        try:
            self.make_new_fn_unique()
        except Exception as e:
            raise e

        if self.collision_detected:
            print( "{0} => {1} Destination collision. Aborting.".format(
                os.path.basename(self.old_fn), os.path.basename(self.new_fn)))
            return

        try:
            print( "Moving the files: {0} ==> {1}".format(
                os.path.basename(self.old_fn), os.path.basename(self.new_fn)))
            # XXX: Unit tests did not catch this bug.
            # os.rename(self.old_fn, self.new_fn)
            os.rename(self.old_fn_fq, self.new_fn_fq)
        except OSError as e:
            print("Unable to rename file: {0}".format(e.strerror),
                    file=sys.stderr)

    def make_new_fn_unique(self):
        """Check new_fn for uniqueness in 'workdir'. Rename, adding a numerical
        suffix until it is unique.
        """

        # Rename file by appending number if we have collision.
        # TODO: I wish I didn't specify \d+_\d+ for the first part. perhaps not
        # -\d\ before .jpg would be better for the second
        # match.
        new_fn = self.new_fn
        counter = 1
        while(os.path.exists(self.new_fn_fq)):
            if (self.old_fn == self.new_fn):
                # Same file, faux collision.
                break
            if (not self.avoid_collisions):
                # Do not attempt to rename.
                self.collision_detected = True
                break
            new_fn = re.sub(r'^(\d+_\d+)-\d+\.jpg',
                    r'\1-{0}.jpg'.format(counter), self.new_fn)
            new_fn = re.sub(r'^(\d+_\d+)\.jpg',
                    r'\1-{0}.jpg'.format(counter), self.new_fn)
            counter += 1
            if counter > self.MAX_RENAME_ATTEMPTS:
                raise Exception("Too many rename attempts: {0}".format(self.new_fn))
            self.new_fn_fq = os.path.join(self.workdir, new_fn)
        self.new_fn = new_fn
        self.new_fn_fq = os.path.join(self.workdir, new_fn)


class FileMapList():
    """Intelligently add FileMap() instances to file_map list based on order
    of instance.new_fn attributes."""

    def __init__(self):
        self.file_map = []

    def add(self, instance):
        """Add, whether insert or append, a FileMap instance to the file_map
        list in the order of instance.new_fn. If there are duplicate new_fn
        in the list, they will be resolved in instance.move().
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
        """TODO: Define a generator function here to return items on the
        file_map list.
        """
        pass


def init_file_map(workdir, avoid_collisions=None):
    """Read the work directory looking for files with extensions defined in the
    EXTENSIONS constant. Note that this could use a more elaborate magic
    number mechanism that would be cool.

    Arguments:
        str: workdir - The directory in which all activity will occur.

    Returns:
        list: file_map - List of FileMap instances.
    """

    # List of FileMap objects.
    file_map = FileMapList()

    # Initialize file_map list.
    for extension in EXTENSIONS:
        for filename in glob.glob(os.path.join(workdir,
                '*.{0}'.format(extension))):
            try:
                file_map.add(FileMap(filename, avoid_collisions))
            except Exception as e:
                print("{0}".format(e.message), file=sys.stderr)

    return file_map


def process_file_map(file_map, simon_sez=None, move_func=None):
    """Iterate through the Python list of FileMap objects. Move the file if
    Simon sez.

    Arguments:
        str: workdir - Working directory.
        dict: file_map - old_fn to new_fn mapping.
        boolean: simon_sez - Dry run or real thing.
        func: move_func - Move function to use for testing or default.
    Returns:
        None

    >>> filemap = FileMap('IMG0332.JPG', avoid_collisions=None, exif_data={'DateTimeOriginal': '2014-08-18 20:23:83'})
    >>> def move_func(old_fn, new_fn): pass
    >>> file_map_list = FileMapList()
    >>> file_map_list.add(filemap)
    >>> process_file_map(file_map_list, True, move_func)

    """

    # XXX: Of marginal utility
    if simon_sez is None:
        simon_sez = False

    for fm in file_map.file_map:
        try:
            if simon_sez:
                if move_func is None:
                    fm.move()
                else:
                    move_func(fm.old_fn, fm.new_fn)
            else:
                if fm.old_fn != fm.new_fn:
                    print("DRY RUN: {0} ==> {1}".format(fm.old_fn, fm.new_fn))
                    fm.same_files = False   # For unit test only.
        except Exception as e:
            print("{0}".format(e.message), file=sys.stderr)
            break


def process_all_files(workdir=None, simon_sez=None, avoid_collisions=None):
    """Manage the entire process of gathering data and renaming files."""

    if workdir is None:
        workdir = os.path.dirname(os.path.abspath(__file__))

    if not os.path.exists(workdir):
        print("Directory {0} does not exist. Exiting.",format(workdir),
                file=sys.stderr)
        sys.exit(1)

    if not os.access(workdir, os.W_OK):
        print("Directory {0} is not writable. Exiting.".format(workdir),
                file=sys.stderr)
        sys.exit(1)

    file_map = init_file_map(workdir, avoid_collisions)
    process_file_map(file_map, simon_sez)


def main():
    """Parse command-line arguments. Initiate file processing."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--simon-sez",
            help="Really, Simon sez rename the files!", action="store_true")
    parser.add_argument("-a", "--avoid-collisions",
            help="Rename until filenames do not collide. Danger!", action="store_true")
    parser.add_argument("-d", "--directory",
            help="Read files from this directory.")
    args = parser.parse_args()
    process_all_files(workdir=args.directory, simon_sez=args.simon_sez,
            avoid_collisions=args.avoid_collisions)

if __name__ == '__main__':  # pragma: no cover
    main()
