import os
import unittest
import unittest.mock as mock

from python_project_wizard.build_project.directories import *
from python_project_wizard.build_project.name import *
from python_project_wizard.project import Project


class DirectoriesTestSuite(unittest.TestCase):
    def test_constructor(self):
        project = Project(name="merlin project")
        cwd = os.getcwd()
        directories = Directories(project)
        self.assertEqual(
            directories.main,
            os.path.join(cwd, main_directory(project.name)),
        )
        self.assertEqual(
            directories.source,
            os.path.join(
                cwd,
                main_directory(project.name),
                source_directory(project.name),
            ),
        )
        self.assertEqual(
            directories.dot_vscode,
            os.path.join(cwd, main_directory(project.name), ".vscode"),
        )
        self.assertEqual(
            directories.test,
            os.path.join(
                cwd,
                main_directory(project.name),
                source_directory(project.name),
                "test",
            ),
        )
