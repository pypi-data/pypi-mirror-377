import unittest

from python_project_wizard.answer import Answer


class AnswerTestSuite(unittest.TestCase):
    def test_constructor(self):
        self.assertIsInstance(Answer(""), Answer)
