JPEG Rename Utility
===================
Demo code written for SLC Python.

``jpeg_rename.py`` will find all ``{*jpg|*jpeg|*JPG}`` files in ``DIRECTORY``. It
will then read the ``DateTimeOriginal`` EXIF tag. Each found file will be
renamed using the EXIF data.

``jpeg_rename.py`` is useful when combining digital photographs from different
sources like a mobile phone and a Canon point and shoot camera for instance.
The photographs from the phone are named ``YYYYMMDD_HHMMSS.jpg`` while the
Canon camera photographs are name ``IMG_nnnn.JPG``. Other variations on this
theme have led to the creation of this utility.

It began as a 4-line shell script using the ``exiftags`` program combined with
``sed`` and ``awk``. Trouble was that name collisions were potentially tragic
and other features were missing.


Installation
============

Create a virtual environment. These instructions assume ``virtualenvwrapper``::

    cd $PROJECT_HOME
    mkvirtualenv jpeg_rename
    setvirtualenvproject
    pip install -r requirements.txt


Usage
=====

Get usage help like this::

    ./jpeg_rename.py --help
    usage: jpeg_rename.py [-h] [-s] [-a] [-d DIRECTORY]

    optional arguments:
      -h, --help            show this help message and exit
      -s, --simon-sez       Really, Simon sez rename the files!
      -a, --avoid-collisions
                            Rename until filenames do not collide. Danger!
      -d DIRECTORY, --directory DIRECTORY
                            Read files from this directory.

If only ``--directory`` is specified, ``jpeg_rename.py`` will output what it
would do if ``--simon-sez`` were also specified. It will indicate ``DRY RUN``
in the output.

``jpeg_rename.py`` will avoid filename collisions by appending ``_#`` to
filenames as needed. Since this behavior can be troublesome, it will not occur
unless explicitly requested with ``--avoid-collisions`` on the command line.
If not requested, ``jpeg_rename.py`` will warn of collisions only. In this
case, ``jpeg_rename.py`` may be safely re-run with ``--avoid-collisions`` to
rename the leftovers.

Run Tests
=========

Run the doctests using the ``doctest.sh`` shell script.::

    sh doctest.sh

Unit tests are implemented with Pytest and coverage. Run the unit tests with
coverage using the 'pytest_with_coverage.sh' shell script::

    sh pytest_with_coverage.sh

Coverage reports will be written to ``./htmlcov``. View the report by opening
``./htmlcov/index.html`` with your favorite browser.
