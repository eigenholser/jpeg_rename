import os
import sys
import pytest
from mock import Mock, patch
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../')

from photo_rename.rename import *
from .stubs import *
from . import TEST_RENAME_MAIN


class StubArgs(object):
    """
    Stub class.
    """

    def __init__(self, directory='.', simon_sez=False, verbose=False,
            mapfile=None):

        self.directory = directory
        self.simon_sez = simon_sez
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


class TestRenameMain(object):
    """
    Tests for main() function.
    """
    skiptests = not TEST_RENAME_MAIN

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.rename.argparse.ArgumentParser')
    @patch('photo_rename.rename.process_all_files')
    def test_main_function(self, m_process_all_files, m_argparser):
        """
        Test main() function. Mock argparse and replace with stubs. Verify
        process_all_files called with expected arguments.
        """
        myargs = StubArgs()
        m_argparser.return_value = StubArgumentParser(myargs)
        retval = main()
        m_process_all_files.assert_called_with(workdir='.', simon_sez=False,
                mapfile=None)

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @patch('photo_rename.rename.argparse.ArgumentParser')
    @patch('photo_rename.rename.os.path.dirname')
    @patch('photo_rename.rename.os.path.exists')
    @patch('photo_rename.rename.os.access')
    @patch('photo_rename.rename.process_all_files')
    def test_workdir_is_none(self, m_process_all_files, m_access,
            m_exists, m_dirname, m_argparse):
        """
        Test main() function. Test process_all_files called with expected
        arguments.
        """
        workdir = "abc"
        mapfile = "foo"
        myargs = StubArgs(directory=None, mapfile=mapfile)
        m_argparse.return_value = StubArgumentParser(myargs)
        m_access = True
        m_exists.return_value = True
        m_dirname.return_value = workdir
        retval = main()
        m_process_all_files.assert_called_with(workdir=workdir,
                simon_sez=False, mapfile=mapfile)

    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize(
            "directory, simon_sez, verbose", [
            (None, False, False),
            (None, True, True),
            ("foo", False, False),
        ])
    @patch('photo_rename.rename.argparse.ArgumentParser')
    @patch('photo_rename.rename.os.path.dirname')
    @patch('photo_rename.rename.os.path.exists')
    @patch('photo_rename.rename.os.access')
    @patch('photo_rename.rename.sys.exit')
    @patch('photo_rename.rename.process_all_files')
    def test_workdir_is_not_none(self, m_process_all_files, m_exit,
            m_access, m_exists, m_dirname, m_argparse,
            directory, simon_sez, verbose):
        """
        Test main() function. Test process_all_files called with expected
        arguments.
        """
        workdir = "abc"
        mapfile = "foo"
        myargs = StubArgs(directory=directory, simon_sez=simon_sez,
            verbose=verbose, mapfile=mapfile)
        m_argparse.return_value = StubArgumentParser(myargs)
        m_access.return_value = True
        m_exists.return_value = True
        m_dirname.return_value = workdir
        retval = main()
        if directory:
            m_exit.assert_called_once
        else:
            m_process_all_files.assert_called_with(workdir=workdir,
                simon_sez=simon_sez, mapfile=mapfile)


    @pytest.mark.skipif(skiptests, reason="Work in progress")
    @pytest.mark.parametrize(
            "path_exists, os_access", [
            (False, True,),
            (True, False,),
            (True, True),
        ])
    @patch('photo_rename.rename.argparse.ArgumentParser')
    @patch('photo_rename.rename.os.path.dirname')
    @patch('photo_rename.rename.os.path.exists')
    @patch('photo_rename.rename.os.access')
    @patch('photo_rename.rename.sys.exit')
    @patch('photo_rename.rename.process_all_files')
    def test_mapfile_errors(self, m_process_all_files, m_exit,
            m_access, m_exists, m_dirname, m_argparse,
            path_exists, os_access):
        """
        Test main() function.
        """
        workdir = "abc"
        mapfile = "foo"
        myargs = StubArgs(directory=None, simon_sez=None,
            verbose=None, mapfile=mapfile)
        m_argparse.return_value = StubArgumentParser(myargs)
        m_access.return_value = os_access
        m_exists.return_value = path_exists
        m_dirname.return_value = workdir
        retval = main()
        if path_exists and os_access:
            m_exit.assert_not_called
        else:
            m_exit.assert_called_once

