import unittest
from dataclasses import dataclass, field

from python_project_wizard.field import set_field


@dataclass
class TestResult:
    name: str = field(init=False)


class SetFieldTestSuite(unittest.TestCase):
    def test_set_field(self):
        test_name = "BEANS"
        test_result = TestResult()
        test_result = set_field(test_result, "name", test_name)
        self.assertEqual(test_result.name, test_name)
