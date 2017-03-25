import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename import *
from stubs import *


class StubArgs(object):
    """
    Stub class.
    """

    def __init__(self, directory='.', simon_sez=False,
        avoid_collisions=False, verbose=False, mapfile=None):

        self.directory = directory
        self.simon_sez = simon_sez
        self.avoid_collisions = avoid_collisions
        self.verbose = verbose
        self.mapfile = mapfile


class StubArgumentParser(object):
    """Stub class."""

    def __init__(self, myargs):
        self.myargs = myargs

    def add_argument(self, *args, **kwargs):
        """Stub method."""
        pass

    def parse_args(self):
        """Stub method."""
        return self.myargs


class TestMainFunction(object):
    """
    Tests for main() function.
    """

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @patch('photo_rename.argparse.ArgumentParser')
    @patch('photo_rename.process_all_files')
    def test_main_function(self, mock_process_all_files, mock_argparser):
        """
        Test main() function. Mock argparse and replace with stubs. Verify
        process_all_files called with expected arguments.
        """
        myargs = StubArgs()
        mock_argparser.return_value = StubArgumentParser(myargs)
        retval = main()
        mock_process_all_files.assert_called_with(workdir='.', simon_sez=False,
                avoid_collisions=False, mapfile=None)

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @patch('photo_rename.argparse.ArgumentParser')
    @patch('photo_rename.os.path.dirname')
    @patch('photo_rename.os.path.exists')
    @patch('photo_rename.os.access')
    @patch('photo_rename.process_all_files')
    def test_workdir_is_none(self, mock_process_all_files, mock_access,
            mock_exists, mock_dirname, mock_argparse):
        """
        Test main() function. Test process_all_files called with expected
        arguments.
        """
        workdir = "abc"
        mapfile = "foo"
        myargs = StubArgs(directory=None, mapfile=mapfile)
        mock_argparse.return_value = StubArgumentParser(myargs)
        mock_access = True
        mock_exists.return_value = True
        mock_dirname.return_value = workdir
        retval = main()
        mock_process_all_files.assert_called_with(workdir=workdir,
                simon_sez=False, avoid_collisions=False, mapfile=mapfile)

    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @pytest.mark.parametrize(
            "directory, simon_sez, verbose, avoid_collisions", [
            (None, False, False, False),
            (None, True, True, True),
            ("foo", False, False, False),
        ])
    @patch('photo_rename.argparse.ArgumentParser')
    @patch('photo_rename.os.path.dirname')
    @patch('photo_rename.os.path.exists')
    @patch('photo_rename.os.access')
    @patch('photo_rename.sys.exit')
    @patch('photo_rename.process_all_files')
    def test_workdir_is_not_none(self, mock_process_all_files, mock_exit,
            mock_access, mock_exists, mock_dirname, mock_argparse,
            directory, simon_sez, verbose, avoid_collisions):
        """
        Test main() function. Test process_all_files called with expected
        arguments.
        """
        workdir = "abc"
        mapfile = "foo"
        myargs = StubArgs(directory=directory, simon_sez=simon_sez,
            verbose=verbose, avoid_collisions=avoid_collisions,
            mapfile=mapfile)
        mock_argparse.return_value = StubArgumentParser(myargs)
        mock_access.return_value = True
        mock_exists.return_value = True
        mock_dirname.return_value = workdir
        retval = main()
        if directory:
            mock_exit.assert_called_once
        else:
            mock_process_all_files.assert_called_with(workdir=workdir,
                simon_sez=simon_sez, avoid_collisions=avoid_collisions,
                mapfile=mapfile)


    @pytest.mark.skipif(RUN_TEST, reason="Work in progress")
    @pytest.mark.parametrize(
            "path_exists, os_access", [
            (False, True,),
            (True, False,),
            (True, True),
        ])
    @patch('photo_rename.argparse.ArgumentParser')
    @patch('photo_rename.os.path.dirname')
    @patch('photo_rename.os.path.exists')
    @patch('photo_rename.os.access')
    @patch('photo_rename.sys.exit')
    @patch('photo_rename.process_all_files')
    def test_mapfile_errors(self, mock_process_all_files, mock_exit,
            mock_access, mock_exists, mock_dirname, mock_argparse,
            path_exists, os_access):
        """
        Test main() function.
        """
        workdir = "abc"
        mapfile = "foo"
        myargs = StubArgs(directory=None, simon_sez=None,
            verbose=None, avoid_collisions=None,
            mapfile=mapfile)
        mock_argparse.return_value = StubArgumentParser(myargs)
        mock_access.return_value = os_access
        mock_exists.return_value = path_exists
        mock_dirname.return_value = workdir
        retval = main()
        if path_exists and os_access:
            mock_exit.assert_not_called
        else:
            mock_exit.assert_called_once

