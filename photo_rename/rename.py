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


def process_all_files(
        workdir=None, simon_sez=None, mapfile=None):
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

    harvester = Harvester(workdir, mapfile)
    file_map = harvester["filemaps"]
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
            mapfile=mapfile)


if __name__ == '__main__':  # pragma: no cover
    main()
