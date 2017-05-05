import argparse
import logging
import os
import re
import stat
import sys
import pyexiv2
import photo_rename
from photo_rename import Filemap, FilemapList, Harvester
from photo_rename.utils import CustomArgumentParser


logger = logging.getLogger(__name__)


def process_all_files(workdir, simon_sez=None):
    """
    Manage the entire process of gathering data and renaming files.
    """
    if not os.path.exists(workdir):
        logging.error(
                "Directory {0} does not exist. Exiting.".format(workdir))
        sys.exit(1)

    if not os.access(workdir, os.W_OK):
        logging.error(
                "Destination directory {0} is not writable. Exiting.".format(
                    workdir))
        sys.exit(1)

    import pdb; pdb.set_trace()
    harvester = Harvester(workdir)
    filemap = harvester["filemaps"]

    for fm in filemap.get():
        print("{} ==> {}".format(fm.src_fn, fm.dst_fn))

    #harvester.process_file_map(file_map, simon_sez)


def main():
    """
    Parse command-line arguments. Initiate file processing.
    """
    parser = CustomArgumentParser() #argparse.ArgumentParser()
    parser.add_argument("-s", "--simon-sez",
            help="Really, Simon sez copy the data!", action="store_true")
    parser.add_argument("-d", "--directory",
            help="Set EXIF DateTimeOriginal/XMP on files in this directory.")
    parser.add_argument("-t", "--timestamp", help="Initial timestamp.")
    parser.add_argument("-i", "--interval",
            help="Interval in seconds to use for successive files.")
    parser.add_argument("-v", "--verbose", help="Log level to DEBUG.",
            action="store_true")
    myargs = parser.parse_args()

    if myargs.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    workdir = myargs.directory

    if not workdir:
        logging.error("Exiting due to errors.")
        parser.usage_message()
        sys.exit(1)

    process_all_files(workdir, simon_sez=myargs.simon_sez)


if __name__ == '__main__':  # pragma: no cover
    main()
