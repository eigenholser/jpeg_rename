import argparse
import logging
import os
import re
import stat
import sys
import pyexiv2
import photo_rename
from photo_rename import FileMetadata, Harvester
from photo_rename.utils import CustomArgumentParser


logger = logging.getLogger(__name__)


def process_all_files(src_directory, dst_directory, simon_sez=None):
    """
    Manage the entire process of gathering data and renaming files.
    """
    if not os.path.exists(src_directory):
        logging.error(
                "Directory {0} does not exist. Exiting.".format(
                    src_directory))
        sys.exit(1)

    if not os.access(dst_directory, os.W_OK):
        logging.error(
                "Destination directory {0} is not writable. Exiting.".format(
                    dst_directory))
        sys.exit(1)

    harvester = Harvester(src_directory, metadata_dst_directory=dst_directory)
    filemap = harvester["filemaps"]

    for fm in filemap.get():
        logger.info(
                "Copying metadata from {} ==> {}".format(
                    fm.src_fn, fm.dst_fn))
        src_fmd = FileMetadata(os.path.join(src_directory, fm.src_fn))
        src_fmd.copy_metadata(os.path.join(dst_directory, fm.dst_fn))


def main():
    """
    Parse command-line arguments. Initiate file processing.
    """
    parser = CustomArgumentParser() #argparse.ArgumentParser()
    parser.add_argument("-s", "--simon-sez",
            help="Really, Simon sez copy the data!", action="store_true")
    parser.add_argument("-r", "--src-directory",
            help="Copy metadata from files in this directory.")
    parser.add_argument("-d", "--dst-directory",
            help="Copy metadata to matching files in this directory.")
    parser.add_argument("-v", "--verbose", help="Log level to DEBUG.",
            action="store_true")
    myargs = parser.parse_args()

    if myargs.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    error = False

    if error:
        logging.error("Exiting due to errors.")
        parser.usage_message()
        sys.exit(1)

    # TODO: validate src/dst directory args.
    src_directory = myargs.src_directory
    dst_directory = myargs.dst_directory

    process_all_files(src_directory, dst_directory,
            simon_sez=myargs.simon_sez)


if __name__ == '__main__':  # pragma: no cover
    main()
