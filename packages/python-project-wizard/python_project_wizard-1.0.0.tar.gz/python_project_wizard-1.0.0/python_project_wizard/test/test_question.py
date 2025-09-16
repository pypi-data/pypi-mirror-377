import unittest

from python_project_wizard.question.bool_question import BoolQuestion
from python_project_wizard.question.plain_question import PlainQuestion
from python_project_wizard.question.question import Question
from python_project_wizard.question.version_question import VersionQuestion


class QuestionTestSuite(unittest.TestCase):
    def test_constructor(self):
        self.assertIsInstance(PlainQuestion("Name?"), Question)
        self.assertIsInstance(PlainQuestion("Name?", "Merlin"), Question)
        self.assertIsInstance(BoolQuestion("Name?"), Question)
        self.assertIsInstance(BoolQuestion("Name?", "Y"), Question)

    def test_name_validator(self):
        raw_input = "merlin"
        question = PlainQuestion("")
        answer = question.validate_input_or_default(raw_input)
        self.assertEqual(answer.value, raw_input)

    def test_yes_or_no_validator_true_values(self):
        raw_inputs = ["Y", "y", "Yes", "Yeah", "yes", "yup", "you"]
        question = BoolQuestion("")
        for raw_input in raw_inputs:
            answer = question.validate_input_or_default(raw_input)
            self.assertTrue(answer.value)

    def test_yes_or_no_validator_false_values(self):
        raw_inputs = ["N", "n", "No", "no", "Nah", "nay"]
        question = BoolQuestion("")
        for raw_input in raw_inputs:
            answer = question.validate_input_or_default(raw_input)
            self.assertFalse(answer.value)

    def test_yes_or_no_validator_error_values(self):
        raw_inputs = ["maybe", "c", "C", "huh"]
        question = BoolQuestion("")
        for raw_input in raw_inputs:
            self.assertRaises(
                ValueError, BoolQuestion.validate_input_or_default, question, raw_input
            )

    def test_set_value_to_default(self):
        test_input = ""
        question = BoolQuestion("Do you use VSCode?", "Y")
        answer = question.validate_raw_input(test_input)
        self.assertIsInstance(answer.value, bool)
        self.assertTrue(answer.value)

    def test_version_valid_values(self):
        # TODO: Validate that my modules work with other version of Python
        test_inputs = ["3.10"]
        question = VersionQuestion("What version of Python?")
        for input in test_inputs:
            answer = question.validate_input_or_default(input)
            self.assertEqual(input, answer.value)

    def test_version_error_values(self):
        test_inputs = ["2.7", "3.", "3"]
        question = VersionQuestion("What version of Python?")
        for input in test_inputs:
            self.assertRaises(
                ValueError, VersionQuestion.validate_input_or_default, question, input
            )

    def test_default_is_valid(self):
        self.assertRaises(ValueError, BoolQuestion, "", "huh")
        self.assertRaises(ValueError, VersionQuestion, "", "2.7")
