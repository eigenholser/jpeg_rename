import argparse
import logging
import os
import re
import stat
import sys
import pyexiv2
import photo_rename
from photo_rename import FileMap, FileMapList, Harvester


logger = logging.getLogger(__name__)


def read_alt_file_map(mapfile, delimiter='\t', lineterm=None):
    """
    Read a filename map for the purpose of transforming the filenames as an
    alternative to using EXIF/XMP metadata DateTime information. Only require
    map file as an absolute path.
    """
    with open(mapfile, 'r') as f:
        lines = [line for line in f.readlines() if not line.startswith('#')]

    if lineterm is None:
        lineterm = get_line_term(lines)

    # Get a list of destination filenames from map so we can check for dupes.
    # This may seem pedantic but it will avoid a lot of trouble if there is a
    # duplicate new filename because of human error.
    files = [str.split(line.rstrip(lineterm), delimiter)[1] for line in lines]
    if scan_for_dupe_files(files):
        raise Exception(
            "Duplicate destination filename detected: {}".format(ofn))

    # XXX: This is soooo cool! List of lists flattened all on one nested
    # comprehension.
    # [[k1, v1], [k2, v2], ..., [kn, vn]] --> {k1: v1, k2: v2, ..., kn: vn}
    return dict(zip(*[iter([x for sublist in [
        str.split(line.rstrip(lineterm), delimiter) for line in lines]
        for x in sublist])] * 2))


def get_line_term(lines):
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

def scan_for_dupe_files(files):
    """
    O(n^2) scan of desination list for duplicates. Used when processing a map
    file. Returns True if duplicate files.
    """
    for ofile in files:
        count = 0
        for ifile in files:
            if ofile == ifile:
                count += 1
            if count > 1:
                return True
    return False


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

    harvester = Harvester()
    file_map = harvester.init_file_map(workdir, mapfile, avoid_collisions)
    harvester.process_file_map(file_map, simon_sez)


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

    if (myargs.verbose):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Use current directory if --directory not specified.
    workdir = myargs.directory
    if workdir is None:
        workdir = os.getcwd()
        logging.info(
                "--directory not given. Using workdir={}".format(workdir))

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

    process_all_files(workdir=workdir, simon_sez=myargs.simon_sez,
            avoid_collisions=myargs.avoid_collisions, mapfile=mapfile)


if __name__ == '__main__':  # pragma: no cover
    main()
