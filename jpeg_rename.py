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


class FileMap():
    """FileMap represents a mapping between the old_fn and the new_fn. It's
    methods perform all necessary instance functions for the rename.

    Arguments:
        str: old_fn - Old Filename
        dict: exif_data - For testing only. Dict with sample EXIF data.
    """

    def __init__(self, old_fn, exif_data=None):
        """
        >>> filemap = FileMap('abc123.jpeg', {})
        >>> filemap.old_fn
        'abc123.jpeg'
        >>> filemap.new_fn
        'abc123.jpg'
        >>>
        """
        self.old_fn_fq = old_fn
        self.workdir = os.path.dirname(old_fn)
        self.old_fn = os.path.basename(old_fn)

        # Read EXIF data from old filename
        if exif_data is None:
            self.read_exif_data()
        else:
            self.exif_data = exif_data

        self.get_new_fn()
        self.make_new_fn_unique()

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

    def get_new_fn(self):
        """Generate new filename from old_fn EXIF data if possible. Even if not
        possible, lowercase old_fn and normalize file extension.

        Arguments:
            dict: EXIF data

        Returns:
            str: Filename derived from EXIF data.

        >>> filemap = FileMap('abc123.jpeg', {'DateTimeOriginal': '2014:08:16 06:20:30'})
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

        print( "Really moving the files: {0} ==> {1}".format(
            os.path.basename(self.old_fn), os.path.basename(self.new_fn)))

        # TODO: for now we're just printing what we would do.
        return

        try:
            os.rename(old_fn, new_fn)
        except Exception:
            print("Unable to rename file: {0}".format(e.message), file=sys.stderr)

    def make_new_fn_unique(self):
        """Check new_fn for uniqueness in 'workdir'. Rename, adding a numerical
        suffix until it is unique.
        """

        # Rename file by appending number if we have collision.
        # TODO: I wish I didn't specify \d+_\d+ for the first part.
        # perhaps not -\d\ before .jpg would be better for the second
        # match.
        new_fn = self.new_fn
        counter = 1
        while(os.path.exists(self.new_fn_fq)):
            if (self.old_fn == self.new_fn):
                break
            new_fn = re.sub(r'^(\d+_\d+)-\d+\.jpg',
                    r'\1-{0}.jpg'.format(counter), self.new_fn)
            new_fn = re.sub(r'^(\d+_\d+)\.jpg',
                    r'\1-{0}.jpg'.format(counter), self.new_fn)
            counter += 1
            self.new_fn_fq = os.path.join(self.workdir, new_fn)
        self.new_fn = new_fn
        self.new_fn_fq = os.path.join(self.workdir, new_fn)


def init_file_map(workdir):
    """Read the work directory looking for files with extensions defined in the
    EXTENSIONS constant. Note that this could use a more elaborate magic
    number mechanism that would be cool.
    """

    # Dict with old_fn ==> new_fn mapping.
    file_map = []

    # Initialize file_map dict.
    for extension in EXTENSIONS:
        for filename in glob.glob(os.path.join(workdir,
                '*.{0}'.format(extension))):
            file_map.append(FileMap(filename))

    return file_map


def process_file_map(file_map, clobber, move_func=None):
    """Iterate through the Python dict that maps old filenames to new
    filenames. Move the file if Simon sez.

    Arguments:
        str: workdir - Working directory.
        dict: file_map - old_fn to new_fn mapping.
        boolean: clobber - Dry run or real thing.
        func: move_func - Move function to use for testing or default.
    Returns:
        None

    >>> filemap = FileMap('IMG0332.JPG', {'DateTimeOriginal': '2014-08-18 20:23:83'})
    >>> def move_func(old_fn, new_fn): pass
    ...
    >>> process_file_map([filemap], True, move_func)
    >>>

    """

    for fm in file_map:
        try:
            if clobber:
                if move_func is None:
                    fm.move()
                else:
                    move_func(fm.old_fn, fm.new_fn)
        except Exception as e:
            print("{0}".format(e.message), file=sys.stderr)
            break


def process_all_files(workdir=None, clobber=None):
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

    if clobber is None:
        clobber = False

    file_map = init_file_map(workdir)
    process_file_map(file_map, clobber)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--clobber",
            help="Really, Simon sez rename the files!", action="store_true")
    parser.add_argument("-d", "--directory",
            help="Read files from this directory.")
    args = parser.parse_args()
    process_all_files(workdir=args.directory, clobber=args.clobber)

