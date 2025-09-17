import os
import shutil
import unittest
import unittest.mock as mock

from python_project_wizard.build_project.name import *
from python_project_wizard.project import Project


class DirectoryNameTestSuite(unittest.TestCase):
    def test_project_directory_name(self):
        self.assertEqual("Merlin", main_directory("Merlin"))
        self.assertEqual("Merlin", main_directory("merlin"))
        self.assertEqual("MerlinProject", main_directory("merlin project"))

    def test_project_source_name(self):
        self.assertEqual("merlin", source_directory("Merlin"))
        self.assertEqual("merlin", source_directory("merlin"))
        self.assertEqual("merlin_project", source_directory("merlin project"))
