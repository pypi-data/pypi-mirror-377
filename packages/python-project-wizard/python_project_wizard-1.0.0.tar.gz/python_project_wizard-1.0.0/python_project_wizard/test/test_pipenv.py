import os
import unittest
import unittest.mock as mock

import subprocess

from python_project_wizard.build_project.directories import *
from python_project_wizard.build_project.pipenv import *


class PipenvTestSuite(unittest.TestCase):
    @mock.patch("python_project_wizard.build_project.pipenv.install_packages")
    @mock.patch("python_project_wizard.build_project.pipenv.initialize_pipenv")
    def test_create_pipenv(self, mock_init: mock.Mock, mock_install: mock.Mock):
        project = Project(name="merlin project", python_version="3.10")
        dirs = Directories(project)
        create_pipenv(project, dirs)
        mock_init.assert_called_once_with(project, dirs)
        mock_install.assert_called_once_with(project, dirs)

    @mock.patch("subprocess.run")
    def test_initialize_pipenv(self, mocked_run: mock.Mock):
        project = Project(name="merlin project", python_version="3.10")
        cwd = os.getcwd()
        dirs = Directories(project)
        initialize_pipenv(project, dirs)
        mocked_run.assert_any_call(
            ["pipenv", "install", "--python", "3.10"], cwd=dirs.main
        )

    @mock.patch("subprocess.run")
    def test_install_pipenv_package(self, mocked_run: mock.Mock):
        project = Project(
            name="merlin project", python_version="3.10", use_black_formatting=True
        )
        cwd = os.getcwd()
        dirs = Directories(project)
        install_packages(project, dirs)
        mocked_run.assert_any_call(["pipenv", "install", "-d", "black"], cwd=dirs.main)

    @mock.patch("subprocess.run")
    def test_install_pipenv_package(self, mocked_run: mock.Mock):
        project = Project(name="merlin project", python_version="3.10")
        dirs = Directories(project)
        install_packages(project, dirs)
        mocked_run.assert_not_called()
