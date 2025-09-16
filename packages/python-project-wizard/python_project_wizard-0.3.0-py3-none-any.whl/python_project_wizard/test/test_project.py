import unittest

from python_project_wizard.project import Project


class ProjectTestSuite(unittest.TestCase):
    def test_default_constructor(self):
        self.assertIsInstance(Project(), Project)

    def test_set_name(self):
        project_name = "Merlin"
        project = Project(name=project_name)
        self.assertEqual(project_name, project.name)

    def test_set_python_version(self):
        python_version = "3.10"
        project = Project(python_version=python_version)
        self.assertEqual(python_version, project.python_version)

    def test_set_use_black_formatting(self):
        use_black_formatting = True
        project = Project(use_black_formatting=use_black_formatting)
        self.assertEqual(use_black_formatting, project.use_black_formatting)

    def test_set_use_logging(self):
        use_logging = True
        project = Project(use_logging=use_logging)
        self.assertEqual(use_logging, project.use_logging)

    def test_set_use_unittest(self):
        use_unittest = True
        project = Project(use_unittest=use_unittest)
        self.assertEqual(use_unittest, project.use_unittest)

    def test_set_use_configs(self):
        use_configs = True
        project = Project(use_configs=use_configs)
        self.assertEqual(use_configs, project.use_configs)

    def test_set_use_args(self):
        use_args = True
        project = Project(use_args=use_args)
        self.assertEqual(use_args, project.use_args)
