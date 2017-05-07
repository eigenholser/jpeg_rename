Photo Rename Utility
====================

This project is a hobby horse that has practical utility for me. I also use it
in various presentations on programming topics. It was originally written for
a talk Unit Testing in Python for SLC Python.


Installation
============

Create a virtual environment. These instructions assume ``virtualenvwrapper``::

    cd $PROJECT_HOME
    mkvirtualenv photo_rename
    setvirtualenvproject
    pip install -r requirements.txt

Or::

    python setup.py develop


Console Scripts
===============

There are three console scripts.

``pz_rename``
-------------

Find all supported files in ``DIRECTORY``. Currently
the list of supported file types is ARW, JPEG, PNG, and TIFF. It will read
the ``DateTime`` EXIF tag if JPEG, TIFF, ARW, or ``CreateDate`` XMP
tag if PNG. Each found file will be renamed using the metadata. Alternatively,
a map file may be specified which will be used for renaming.

``pz_rename`` is useful when combining digital photographs from different
sources like a mobile phone and a Canon point and shoot camera. It creates a
canonical name using date, time, and possibly a sequence number for
filename collisions.


``pz_copy_metadata``
--------------------
Copy metadata from source filename to destination filename. Files will be
discovered in ``--src-directory``. Matching files will be discovered in
``--dst-directory``. The files are matched after discarding their extensions.
They must be named the same after the extension is removed.

It was inspired by after a bunch of TIFF images with rich metadata were
converted to JPEG but without any metadata. Importing those JPEG images into
a photo manager like Shotwell was not very useful. Copying the metadata from
the TIFF images to the JPEG images solves the problem.


``pz_set_datetime``
-------------------
Set EXIF and XMP datetime information on a collection of photos where it is
missing or otherwise incorrect. Useful for fixing incorrect dates on
photos or just setting dates as needed.


Usage
=====

``pz_rename``
-------------

Get usage help like this::

    pz_rename --help
    usage: pz_rename [-h] [-s] [-a] [-d DIRECTORY]

    optional arguments:
      -h, --help            show this help message and exit
      -s, --simon-sez       Really, Simon sez rename the files!
      -d DIRECTORY, --directory DIRECTORY
                            Read files from this directory.
      -m MAPFILE, --mapfile MAPFILE
                        Use this map to rename files. Do not use metadata.
      -v, --verbose         Log level to DEBUG.

If only ``--directory`` is specified, ``pz_rename`` will output what it
would do if ``--simon-sez`` were also specified. It will indicate ``DRY RUN``
in the output. ``pz_rename`` will **only** operate in the directory
specified.

If ``--mapfile`` is specified, work will be performed in the directory
containing the map file. Option ``--directory`` is not used or permitted when
``--mapfile`` is specified.

``pz_rename`` will avoid filename collisions by appending ``_#`` to
filenames as needed. During the actual file move, a collision will be detected
and no action will be taken.


``pz_copy_metadata``
--------------------

Get usage help like this::

    pz_copy_metadata --help
    usage: pz_copy_metadata [-h] [-s] [-r SRC_DIRECTORY] [-d DST_DIRECTORY] [-v]

    optional arguments:
      -h, --help            show this help message and exit
      -s, --simon-sez       Really, Simon sez copy the data!
      -r SRC_DIRECTORY, --src-directory SRC_DIRECTORY
                            Copy metadata from files in this directory.
      -d DST_DIRECTORY, --dst-directory DST_DIRECTORY
                            Copy metadata to matching files in this directory.
      -v, --verbose         Log level to DEBUG.


``pz_set_datetime``
-------------------

Get usage help like this::

    pz_set_datetime --help
    usage: pz_set_datetime [-h] [-s] [-d DIRECTORY] [-t DATETIME] [-i INTERVAL]
                           [-v]

    optional arguments:
      -h, --help            show this help message and exit
      -s, --simon-sez       Really, Simon sez copy the data!
      -d DIRECTORY, --directory DIRECTORY
                            Set EXIF DateTime/XMP on files in this directory.
      -t DATETIME, --datetime DATETIME
                            Initial datetime YYYY-mm-DD HH:MM:SS.
      -i INTERVAL, --interval INTERVAL
                            Interval in seconds to use for successive files.
      -v, --verbose         Log level to DEBUG.


Map File
========

The map file contains a tab delimited current filename to new filename mapping
on each row. Create any filename you like. It must live with the photos to be
renamed. If ``--mapfile`` is specified, image metadata will not be used.
Filename extensions must not be used in the mapfile.


Run Tests
=========

Run the doctests using the ``doctest.sh`` shell script.::

    sh doctest.sh

Unit tests are implemented with Pytest and coverage. Run the unit tests with
coverage like this::

    pytest

Coverage reports will be written to ``./htmlcov``. View the report by opening
``./htmlcov/index.html`` with your favorite browser.

References
==========
https://python3-exiv2.readthedocs.io/en/latest/api.html
http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/EXIF.html
http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/XMP.html#xmp
