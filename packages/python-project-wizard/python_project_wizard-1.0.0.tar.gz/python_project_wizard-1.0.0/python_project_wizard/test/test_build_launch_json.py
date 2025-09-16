import os
import unittest
import unittest.mock as mock

from python_project_wizard.build_project.get_launch_json_content import *
from python_project_wizard.project import Project


class LaunchJSONContentTestSuite(unittest.TestCase):
    def test_determine_configurations_only_launch(self):
        project = Project(
            name="test project", use_black_formatting=False, use_unittest=False
        )
        expected_configurations = [
            {
                "name": "Launch",
                "type": "python",
                "request": "launch",
                "module": "test_project.main",
                "justMyCode": True,
            }
        ]
        self.assertEqual(determine_configurations(project), expected_configurations)

    def test_determine_configurations_all(self):
        project = Project(
            name="test project", use_black_formatting=True, use_unittest=True
        )
        expected_configs = [
            {
                "name": "Launch",
                "type": "python",
                "request": "launch",
                "module": "test_project.main",
                "justMyCode": True,
            },
            {
                "name": "Format",
                "type": "python",
                "request": "launch",
                "module": "black",
                "justMyCode": True,
                "args": ["test_project"],
            },
            {
                "name": "Test",
                "type": "python",
                "request": "launch",
                "module": "unittest",
                "justMyCode": True,
            },
        ]
        self.assertEqual(determine_configurations(project), expected_configs)

    def test_get_content_minimal(self):
        project = Project(name="test project")
        expected_content = """{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Launch",
      "type": "python",
      "request": "launch",
      "module": "test_project.main",
      "justMyCode": true
    }
  ]
}"""
        self.assertEqual(get_launch_json_content(project), expected_content)
