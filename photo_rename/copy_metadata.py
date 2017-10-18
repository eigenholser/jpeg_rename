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
    error = False

    if not os.path.exists(src_directory):
        logger.error(
                "Directory {0} does not exist. Exiting.".format(
                    src_directory))
        error = True

    if not os.access(dst_directory, os.W_OK):
        logger.error(
                "Destination directory {0} is not writable. Exiting.".format(
                    dst_directory))
        error = True

    if error:
        logger.warn("Exiting due to errors.")
        sys.exit(1)

    harvester = Harvester(src_directory, metadata_dst_directory=dst_directory)
    filemaps = harvester["filemaps"]

    count = 0
    for fm in filemaps.get():
        count += 1
        src_fmd = FileMetadata(os.path.join(src_directory, fm.src_fn))
        if simon_sez:
            logger.info(
                    "Copying metadata from {} ==> {}".format(
                        fm.src_fn, fm.dst_fn))
            src_fmd.copy_metadata(os.path.join(dst_directory, fm.dst_fn))
        else:
            logger.info(
                    "DRY RUN: Copying metadata from {} ==> {}".format(
                        fm.src_fn, fm.dst_fn))
    if count == 0:
        logger.warn("No matching files found. Check src and dst.")

def main():
    """
    Parse command-line arguments. Initiate file processing.
    """
    parser = CustomArgumentParser()
    parser.add_argument("-s", "--simon-sez",
            help="Really, Simon sez copy the data!", action="store_true")
    parser.add_argument("-r", "--src-directory",
            help="Copy metadata from files in this directory.")
    parser.add_argument("-d", "--dst-directory",
            help="Copy metadata to matching files in this directory.")
    parser.add_argument("-v", "--verbose", help="Log level to DEBUG.",
            action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    error = False

    # Require these two arguments.
    for arg in [args.src_directory, args.dst_directory]:
        if not arg:
            logger.error(
                    "Required src or dst directory parameter missing.")
            error = True
            # XXX: Duplicates exit below. Can't check directory if null.
            logger.error("Exiting due to errors.")
            parser.usage_message()
            sys.exit(1)

    if (os.path.exists(args.src_directory) and
            os.path.isdir(args.src_directory)):
        src_directory = args.src_directory
    else:
        logger.error(
            "--src-directory={} does not exist or is not a directory.".format(
                args.dst_directory))
        error = True

    if (os.path.exists(args.dst_directory) and
            os.path.isdir(args.dst_directory)):
        dst_directory = args.dst_directory
    else:
        logger.error(
            "--dst-directory={} does not exist or is not a directory.".format(
                args.dst_directory))
        error = True

    if error:
        logger.error("Exiting due to errors.")
        parser.usage_message()
        sys.exit(1)
    else:
        process_all_files(src_directory, dst_directory, simon_sez=args.simon_sez)


if __name__ == '__main__':  # pragma: no cover
    main()
