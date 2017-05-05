import argparse
import logging
import os
import re
import stat
import sys
import pyexiv2
import photo_rename
from photo_rename import Filemap, FileList, FilemapList
import photo_rename


logger = logging.getLogger(__name__)


class Harvester(object):
    """
    Initialize Filemap list.
    """

    def __init__(self, workdir, mapfile=None, delimiter='\t', lineterm=None,
            metadata_dst_directory=None):
        """
        Set state and initialize list.
        """
        self.workdir = workdir
        self.mapfile = mapfile
        self.delimiter = delimiter
        self.lineterm = lineterm
        self.metadata_dst_directory = metadata_dst_directory
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
        # TODO: This method becoming very cumbersome. Break it up.

        # List of Filemap objects.
        filemaps = FilemapList()
        files = FileList()

        list_workdir = os.listdir(self.workdir)
        if self.mapfile:
            # Extract files in workdir that match against our alternate file
            # map.
            #
            # alt_file_map.keys() = ['abc', 'def', 'ghi', 'jkl', 'mno']
            # list_workdir = ['abc.jpg', 'ghi.jpg', 'pqr.jpg']
            # results in...
            # allfiles = ['abc.jpg', 'ghi.jpg']
            alt_file_map = self.read_alt_file_map()
            filename_prefix_map = {}
            for file_prefix in alt_file_map.keys():
                for filename in list_workdir:
                    if re.search(r"^{}\..+$".format(file_prefix), filename):
                        files.add(filename)
                        filename_prefix_map[filename] = file_prefix
                allfiles = [file for file in files.get()]
        else:
            for file_add in list_workdir:
                files.add(file_add)
            allfiles = [file for file in files.get()]


        # TODO: Somewhat of a hack with this new feature. Still sorting it
        # out. This whole method needs chopping apart.
        if self.mapfile and self.metadata_dst_directory:
            # Copying EXIF metadata from src to dst.
            for src_fn in filename_prefix_map.keys():
                for filename in os.listdir(self.metadata_dst_directory):
                    if re.search(r"^{}\..+$".format(
                            filename_prefix_map[src_fn]), filename):
                        src_fn_fq = os.path.join(self.workdir, src_fn)
                        dst_fn_fq = os.path.join(
                                self.metadata_dst_directory, filename)
                        src_fn_ext = os.path.splitext(src_fn)[1][1:]
                        dst_fn_ext = os.path.splitext(filename)[1][1:]
                        # TODO: Image type is meaningless here yet necessary.
                        image_type = photo_rename.EXTENSION_TO_IMAGE_TYPE[
                                src_fn_ext]
                        filemap = Filemap(src_fn_fq, image_type,
                                metadata=None, dst_fn=dst_fn_fq)
                        filemaps.add(filemap)
            return filemaps

        # Initialize file_map list.
        for filename in (allfiles):

            filename_fq = os.path.join(self.workdir, filename)
            if os.path.isdir(filename_fq):
                logger.warn("Skipping directory {0}".format(filename_fq))
                continue

            src_fn_ext = os.path.splitext(filename)[1][1:]
            if src_fn_ext in photo_rename.EXTENSION_TO_IMAGE_TYPE:
                image_type = photo_rename.EXTENSION_TO_IMAGE_TYPE[src_fn_ext]
            else:
                continue

            try:
                if self.mapfile:
                    filename_prefix = filename_prefix_map[filename]
                    dst_fn = "{}.{}".format(
                            alt_file_map[filename_prefix], src_fn_ext)
                    filemaps.add(
                        Filemap(filename_fq, image_type, dst_fn=dst_fn,
                            read_metadata=False))
                else:
                    filemap = Filemap(filename_fq, image_type)
                    filemaps.add(filemap)
            except Exception as e:
                logger.warn("Filemap Error: {0}".format(e))

        # XXX: Here after all Filemap have been initialized we need to check
        # for collisions. Not when mapfile used.
        if not self.mapfile:
            for filemap in [fm for fm in filemaps.get()]:
                dst_fn_fq = os.path.join(self.workdir,
                    self.find_dst_filename_collision(filemaps, filemap))
                filemap.set_dst_fn(dst_fn_fq)

        return filemaps

    def find_dst_filename_collision(self, filemaps, chk_filemap):
        """
        Scan file map list for new destination filename and adjust if
        conflict.
        """
        seq = 1
        dst_fn = chk_filemap.dst_fn
        old_dst_fn = dst_fn
        dst_fn_base = os.path.splitext(dst_fn)[0]
        dst_fn_ext = os.path.splitext(dst_fn)[1][1:]
        dst_fn_regex_s1 = r"^(\d+_\d+)-\d+$"
        dst_fn_regex_s2 = r"^(\d+_\d+)$"
        for filemap in filemaps.get():
            dst_fn_regex_r = r"\1-{0}".format(seq)
            # Stop if we've reached our position.
            if filemap == chk_filemap:
                break
            if dst_fn == filemap.dst_fn:
                dst_fn_base = re.sub(
                        dst_fn_regex_s1, dst_fn_regex_r, dst_fn_base)
                dst_fn_base = re.sub(
                        dst_fn_regex_s2, dst_fn_regex_r, dst_fn_base)
                dst_fn = "{base}.{ext}".format(
                        base=dst_fn_base, ext=dst_fn_ext)
                seq += 1
            if seq > photo_rename.MAX_RENAME_ATTEMPTS:
                raise Exception("Too many rename attempts: {} {}".format(
                    dst_fn, seq))
        if old_dst_fn != dst_fn and chk_filemap.src_fn != dst_fn:
            logger.info("Avoid collision: {} ==> {}".format(
                chk_filemap.src_fn, dst_fn))
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
        Iterate through the Python list of Filemap objects. Move the file if
        Simon sez.

        Arguments:
            str: workdir - Working directory.
            dict: file_map - src_fn to dst_fn mapping.
            boolean: simon_sez - Dry run or real thing.
            func: move_func - Move function to use for testing or default.
        Returns:
            None

        >>> filemap = Filemap('IMG0332.JPG', photo_rename.IMAGE_TYPE_JPEG, metadata={'Exif.Image.DateTime': '2014-08-18 20:23:83'})
        >>> def move_func(src_fn, dst_fn): pass
        >>> filemaps = FilemapList()
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
                        move_func(fm.src_fn, fm.dst_fn)
                else:
                    if fm.src_fn != fm.dst_fn:
                        logging.info("DRY RUN: Moving {0} ==> {1}".format(
                            fm.src_fn, fm.dst_fn))
                        # TODO: Hmm, see about not doing this.
                        fm.same_files = False   # For unit test only.
            except Exception as e:
                logging.info("{0}".format(e))
                break

