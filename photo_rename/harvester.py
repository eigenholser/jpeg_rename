import argparse
import logging
import os
import re
import stat
import sys
import pyexiv2
import photo_rename
from photo_rename import FileMap, FileList, FileMapList


logger = logging.getLogger(__name__)


class Harvester(object):

    def __init__(self, workdir, mapfile=None, avoid_collisions=None,
            delimiter='\t', lineterm=None):
        """
        """
        self.workdir = workdir
        self.mapfile = mapfile
        self.avoid_collisions = avoid_collisions
        self.delimiter = delimiter
        self.lineterm = lineterm
        self.filemaps = self.init_file_map()

    def __getitem__(self, key):
        """
        Implemented for file_map.
        """
        if key == "filemaps":
            return self.filemaps
        raise KeyError("Invalid key")

    def init_file_map(self):
        """
        Read the work directory looking for files with extensions defined in
        the EXTENSIONS constant. Note that this could use a more elaborate
        magic number mechanism that would be cool.
        """

        # List of FileMap objects.
        filemaps = FileMapList()
        files = FileList()

        list_workdir = os.listdir(self.workdir)
        if self.mapfile:
            # Extract files in work dir that match against our alternate file
            # map.
            #
            # alt_file_map.keys() = ['abc', 'def', 'ghi', 'jkl', 'mno']
            # list_workdir = ['abc.jpg', 'ghi.jpg', 'pqr.jpg']
            # results in...
            # all_files_list = ['abc.jpg', 'ghi.jpg']
            alt_file_map = self.read_alt_file_map()
            filename_prefix_map = {}
            for file_prefix in alt_file_map.keys():
                for filename in list_workdir:
                    if re.search(r"^{}\..+$".format(file_prefix), filename):
                        files.add(filename)
                        filename_prefix_map[filename] = file_prefix
                all_files_list = [file for file in files.get()]
        else:
            for file_add in list_workdir:
                files.add(file_add)
            all_files_list = [file for file in files.get()]

        # Initialize file_map list.
        for extension in photo_rename.EXTENSIONS:
            image_regex = r"\." + re.escape(extension) + r"$"
            matching_files = [filename for filename in all_files_list
                    if re.search(image_regex, filename, re.IGNORECASE)]
            logger.debug("Files matching extension {ext}: {files}".format(
                ext=extension, files=matching_files))
            for filename in (matching_files):
                filename_fq = os.path.join(self.workdir, filename)
                # TODO: There once was some trouble here that caused me to
                # comment the directory check. Dunno. Keep an eye on it in
                # case it pops up again in the future.
                if os.path.isdir(filename_fq):
                    logger.warn("Skipping directory {0}".format(filename_fq))
                    continue
                try:
                    image_type = photo_rename.EXTENSION_TO_IMAGE_TYPE[
                            extension]
                    if self.mapfile:
                        filename_prefix = filename_prefix_map[filename]
                        new_fn = "{}.{}".format(
                                alt_file_map[filename_prefix], extension)
                        filemaps.add(
                            FileMap(filename_fq, image_type,
                                self.avoid_collisions, {}, new_fn))
                    else:
                        filemap = FileMap(
                            filename_fq, image_type, self.avoid_collisions)
                        filemap.set_dst_fn(self.find_dst_filename_collision(
                                filemaps, filemap.new_fn))
                        filemaps.add(filemap)
                except Exception as e:
                    logger.warn("FileMap Error: {0}".format(e))
        return filemaps

    def find_dst_filename_collision(self, filemaps, dst_fn):
        """
        Scan file map list for new destination filename and adjust if
        conflict.
        """
        counter = 1
        dst_fn_base = os.path.splitext(dst_fn)[0]
        dst_fn_ext = os.path.splitext(dst_fn)[1][1:]
        dst_fn_regex_s1 = r"^(\d+_\d+)-\d+$"
        dst_fn_regex_s2 = r"^(\d+_\d+)$"
        for filemap in filemaps.get():
            dst_fn_regex_r = r"\1-{0}".format(counter)
            if dst_fn == filemap.new_fn:
                dst_fn_base = re.sub(
                        dst_fn_regex_s1, dst_fn_regex_r, dst_fn_base)
                dst_fn_base = re.sub(
                        dst_fn_regex_s2, dst_fn_regex_r, dst_fn_base)
                dst_fn = "{base}.{ext}".format(
                        base=dst_fn_base, ext=dst_fn_ext)
                counter += 1
            if counter > 10:
                raise Exception("Too many rename attempts: {} {}".format(
                    dst_fn, counter))
        return dst_fn

    def read_alt_file_map(self):
        """
        Read a filename map for the purpose of transforming the filenames as
        an alternative to using EXIF/XMP metadata DateTime information. Only
        require map file as an absolute path.
        """
        # Initialize locally so we do not change instance state.
        lineterm = self.lineterm
        delimiter = self.delimiter

        with open(self.mapfile, 'r') as f:
            lines = [
                line for line in f.readlines() if not line.startswith('#')]

        if lineterm is None:
            lineterm = self.get_line_term(lines)

        # Get a list of destination filenames from map so we can check for
        # dupes. This may seem pedantic but it will avoid a lot of trouble if
        # there is a duplicate new filename because of human error.
        files = [
            str.split(line.rstrip(lineterm), delimiter)[1] for line in lines]
        if self.scan_for_dupe_files(files):
            raise Exception(
                "Duplicate destination filename detected: {}".format(ofn))

        # XXX: This is soooo cool! List of lists flattened all on one nested
        # comprehension.
        # [[k1, v1], [k2, v2], ..., [kn, vn]]
        #                               --> {k1: v1, k2: v2, ..., kn: vn}
        return dict(zip(*[iter([x for sublist in [
            str.split(line.rstrip(lineterm), delimiter) for line in lines]
            for x in sublist])] * 2))

    def get_line_term(self, lines):
        """
        Find line termination style. Require every line to have the same
        termination.
        """
        lineterm = None
        for line in lines:
            if line.endswith('\r\n'):
                term = '\r\n'
            elif line.endswith('\n'):
                term = '\n'
            if lineterm is not None and lineterm != term:
                raise Exception("Inconsistent line termination.")
            else:
                lineterm = term
        return lineterm

    def scan_for_dupe_files(self, files):
        """
        O(n^2) scan of desination list for duplicates. Used when processing a
        map file. Returns True if duplicate files.
        """
        for ofile in files:
            count = 0
            for ifile in files:
                if ofile == ifile:
                    count += 1
                if count > 1:
                    return True
        return False


    def process_file_map(self, file_map, simon_sez=None, move_func=None):
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

        >>> filemap = FileMap('IMG0332.JPG', photo_rename.IMAGE_TYPE_JPEG, avoid_collisions=None, metadata={'Exif.Image.DateTime': '2014-08-18 20:23:83'})
        >>> def move_func(old_fn, new_fn): pass
        >>> filemaps = FileMapList()
        >>> filemaps.add(filemap)
        >>> process_file_map(filemaps, True, move_func)

        """

        # XXX: Of marginal utility
        if simon_sez is None:
            simon_sez = False

        for fm in file_map.get():
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
                        # TODO: Hmm, see about not doing this.
                        fm.same_files = False   # For unit test only.
            except Exception as e:
                logging.info("{0}".format(e))
                break

