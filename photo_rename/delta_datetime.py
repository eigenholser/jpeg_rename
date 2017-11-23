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


def process_all_files(workdir, delta, simon_sez=None):
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
        harvester = Harvester(workdir)
        files = harvester["files"]

        fmds = []
        for fn in files:
            fmd = FileMetadata(os.path.join(workdir, fn))
            fmds.append(fmd)

            original_dt = original_datetime(fmd)

            # Compute delta. Add to start_datetime.
            new_dt = original_dt + timedelta(0, delta)

            # Set the date and time
            msg = "Set datetime: {} : {}".format(
                    fn, new_dt.strftime('%Y:%m:%d %H:%M:%S'))
            if simon_sez:
                fmd.set_datetime(new_dt)
            else:
                msg = "DRY RUN: {}".format(msg)
            logger.info(msg)


def original_datetime(fmd):
    """
    Fetch datatime from image metadata. Compare available datetimes. If they
    are comparable, return datetime. Raise Exception if unable to format.
    """
    original_dt = ""
    metadata = fmd['metadata']
    # TODO: Work out how this will flow. For now just use
    # Exif.Photo.DateTimeOriginal.
    if 'Xmp.xmp.CreateDate' in metadata.keys():
        original_dt = metadata['Xmp.xmp.CreateDate']
        logger.info("Xmp.xmp.CreateDate read: {}".format(original_dt))
    if 'Exif.Image.DateTime' in metadata.keys():
        original_dt = metadata['Exif.Image.DateTime']
        logger.info("Exif.Image.DateTime read: {}".format(original_dt))
    if 'Exif.Photo.DateTimeOriginal' in metadata.keys():
        original_dt = metadata['Exif.Photo.DateTimeOriginal']
        logger.info("Exif.Photo.DateTimeOriginal read: {}".format(original_dt))
    if re.match(r'\d{4}-\d\d-\d\d \d\d:\d\d:\d\d', original_dt):
        return datetime.strptime(original_dt, '%Y-%m-%d %H:%M:%S')

    if re.match(r'\d{4}:\d\d:\d\d \d\d:\d\d:\d\d', original_dt):
        return datetime.strptime(original_dt, '%Y:%m:%d %H:%M:%S')

    # Out of options
    raise Exception("Unrecognized datetime string: {}".format(original_dt))


def main():
    """
    Parse command-line arguments. Initiate file processing.
    """
    parser = CustomArgumentParser()
    parser.add_argument("-s", "--simon-sez",
            help="Really, Simon sez copy the data!", action="store_true")
    parser.add_argument("-d", "--directory",
            help="Set EXIF/XMP DateTime delta on files in this directory.")
    parser.add_argument("-i", "--delta",
            help="Delta in seconds (+/-) to increment datetime.")
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

    if not args.delta:
        logger.error("No time delta specified.")
        error = True
    else:
        delta = int(args.delta)

    if error:
        logger.error("Exiting due to errors.")
        parser.usage_message()
        sys.exit(1)
    else:
        process_all_files(
                workdir, delta, simon_sez=args.simon_sez)


if __name__ == '__main__':  # pragma: no cover
    main()
