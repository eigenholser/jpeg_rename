JPEG Rename Utility
===================
Demo code written for SLC Python.

``photo_rename.py`` will find all JPEG or PNG files in ``DIRECTORY``. It
will then read the ``DateTimeOriginal`` EXIF tag if JPEG, or ``CreateDate``
tag if PNG. Each found file will be renamed using the metadata. Alternatively,
a map file may be specified which will be used for renaming.

``photo_rename.py`` is useful when combining digital photographs from different
sources like a mobile phone and a Canon point and shoot camera for instance.
The photographs from the phone are named ``YYYYMMDD_HHMMSS.jpg`` while the
Canon camera photographs are name ``IMG_nnnn.JPG``. Other variations on this
theme have led to the creation of this utility.

It began as a 4-line shell script using the ``exiftool`` program combined with
``sed`` and ``awk``. Trouble was that name collisions were potentially tragic
and other features were missing.


Installation
============

Create a virtual environment. These instructions assume ``virtualenvwrapper``::

    cd $PROJECT_HOME
    mkvirtualenv photo_rename
    setvirtualenvproject
    pip install -r requirements.txt


Usage
=====

Get usage help like this::

    ./photo_rename.py --help
    usage: photo_rename.py [-h] [-s] [-a] [-d DIRECTORY]

    optional arguments:
      -h, --help            show this help message and exit
      -s, --simon-sez       Really, Simon sez rename the files!
      -a, --avoid-collisions
                            Rename until filenames do not collide. Danger!
      -d DIRECTORY, --directory DIRECTORY
                            Read files from this directory.
      -m MAPFILE, --mapfile MAPFILE
                        Use this map to rename files. Do not use metadata.
      -v, --verbose         Log level to DEBUG.

If only ``--directory`` is specified, ``photo_rename.py`` will output what it
would do if ``--simon-sez`` were also specified. It will indicate ``DRY RUN``
in the output. ``photo_rename.py`` will **only** operate in the directory
specified.

``photo_rename.py`` will avoid filename collisions by appending ``_#`` to
filenames as needed. Since this behavior can be troublesome, it will not occur
unless explicitly requested with ``--avoid-collisions`` on the command line.
If not requested, ``photo_rename.py`` will warn of collisions only. In this
case, ``photo_rename.py`` may be safely re-run with ``--avoid-collisions`` to
rename the leftovers.


Map File
========

The map file contains a tab delimited current filename to new filename mapping
on each row. Create any filename you like. It must live with the photos to be
renamed. If ``--mapfile`` is specified, image metadata will not be used.


Run Tests
=========

Run the doctests using the ``doctest.sh`` shell script.::

    sh doctest.sh

Unit tests are implemented with Pytest and coverage. Run the unit tests with
coverage like this::

    pytest

Coverage reports will be written to ``./htmlcov``. View the report by opening
``./htmlcov/index.html`` with your favorite browser.
