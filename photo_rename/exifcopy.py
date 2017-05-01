import argparse
import logging
import os
import re
import stat
import sys
import pyexiv2
import photo_rename
from photo_rename import Filemap, FilemapList, Harvester


logger = logging.getLogger(__name__)


def process_all_files(workdir, mapfile, dst_directory, simon_sez=None):
    """
    Manage the entire process of gathering data and renaming files.
    """
    if not os.path.exists(workdir):
        logging.error(
                "Directory {0} does not exist. Exiting.".format(workdir))
        sys.exit(1)

    if not os.access(dst_directory, os.W_OK):
        logging.error(
                "Destination directory {0} is not writable. Exiting.".format(
                    workdir))
        sys.exit(1)

    harvester = Harvester(workdir, mapfile,
            metadata_dst_directory=dst_directory)
    file_map = harvester["filemaps"]
    #harvester.process_file_map(file_map, simon_sez)


def main():
    """
    Parse command-line arguments. Initiate file processing.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--simon-sez",
            help="Really, Simon sez copy the data!", action="store_true")
    parser.add_argument("-d", "--dst-directory",
            help="Copy EXIF data to files in this directory.")
    parser.add_argument("-m", "--mapfile",
            help="Use this map to initialize src files.")
    parser.add_argument("-v", "--verbose", help="Log level to DEBUG.",
            action="store_true")
    myargs = parser.parse_args()

    if myargs.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Validate --map
    mapfile = myargs.mapfile
    if mapfile:
        error = False
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

    dst_directory = myargs.dst_directory

    process_all_files(workdir, mapfile, dst_directory,
            simon_sez=myargs.simon_sez)


if __name__ == '__main__':  # pragma: no cover
    main()
