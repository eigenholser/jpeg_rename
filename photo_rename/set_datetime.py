import argparse
from datetime import datetime, timedelta
import logging
import os
import re
import stat
import sys
import pyexiv2
import photo_rename
from photo_rename import Filemap, FilemapList, FileMetadata, Harvester
from photo_rename.utils import CustomArgumentParser


logger = logging.getLogger(__name__)


def process_all_files(workdir, initial_dt, interval, simon_sez=None):
    """
    Manage the entire process of gathering data and renaming files.
    """
    error = False

    if not os.path.exists(workdir):
        logger.error(
                "Directory {0} does not exist. Exiting.".format(workdir))
        error = True

    if not os.access(workdir, os.W_OK):
        logger.error(
                "Destination directory {0} is not writable. Exiting.".format(
                    workdir))
        error = True

    if error:
        logger.warn("Exiting due to errors.")
        sys.exit(1)
    else:
        start_datetime = datetime.strptime(initial_dt, '%Y-%m-%d %H:%M:%S')
        counter = 0

        harvester = Harvester(workdir)
        files = harvester["files"]

        fmds = []
        for fn in files:
            # Compute delta. Add to start_datetime.
            dt_delta = counter * interval
            this_dt = start_datetime + timedelta(0, dt_delta)

            fmd = FileMetadata(os.path.join(workdir, fn))
            fmds.append(fmd)

            logger.info(
                "{} : {}".format(fn, this_dt.strftime('%Y:%m:%d %H:%M:%S')))

            for md in fmd["metadata"].keys():
                if ("Date" in md or "SubSec" in md or "Time" in md or
                        "Offset" in md):
                    logger.debug("{} : {}".format(md, fmd.metadata[md]))

            # Set the date and time
            fmd.set_datetime(this_dt)
            counter += 1


def main():
    """
    Parse command-line arguments. Initiate file processing.
    """
    parser = CustomArgumentParser()
    parser.add_argument("-s", "--simon-sez",
            help="Really, Simon sez copy the data!", action="store_true")
    parser.add_argument("-d", "--directory",
            help="Set EXIF DateTime/XMP on files in this directory.")
    parser.add_argument("-t", "--datetime",
            help="Initial datetime YYYY-mm-DD HH:MM:SS.")
    parser.add_argument("-i", "--interval",
            help="Interval in seconds to use for successive files.")
    parser.add_argument("-v", "--verbose", help="Log level to DEBUG.",
            action="store_true")
    args = parser.parse_args()

    error = False

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Use current directory if --directory not specified.
    workdir = args.directory
    if workdir is None:
        workdir = os.getcwd()
        logger.info(
                "--directory not given. Using workdir={}".format(workdir))

    if not re.match(r'\d{4}-\d\d-\d\d \d\d:\d\d:\d\d', args.datetime):
        logger.error("Invalid datetime. Use YYYY-mm-DD HH:MM:SS.")
        error = True

    if not args.interval:
        # Default to 1 second.
        interval = 1
        logger.warn(
                "--interval not specified. Using {} second interval".format(
                    interval))
    else:
        interval = int(args.interval)

    if error:
        logger.error("Exiting due to errors.")
        parser.usage_message()
        sys.exit(1)
    else:
        process_all_files(
                workdir, args.datetime, interval, simon_sez=args.simon_sez)


if __name__ == '__main__':  # pragma: no cover
    main()
