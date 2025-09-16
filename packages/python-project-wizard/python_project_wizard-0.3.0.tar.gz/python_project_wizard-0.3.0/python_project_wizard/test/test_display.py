import unittest
import unittest.mock as mock
from dataclasses import dataclass

from python_project_wizard.display.console import Console
from python_project_wizard.display.display import Display
from python_project_wizard.question.plain_question import PlainQuestion
from python_project_wizard.question.bool_question import BoolQuestion
from python_project_wizard.question.question import Question


@dataclass
class DefaultStringTest:
    question: Question
    expected: str


class DisplayTestSuite(unittest.TestCase):
    def test_constructor(self):
        self.assertIsInstance(Console(), Display)
        self.assertIsInstance(Console(">"), Display)
        self.assertIsInstance(Console(">", "[ERROR]"), Display)

    def test_prompt_return(self):
        with mock.patch("builtins.print") as mocked_print:
            Console().prompt(PlainQuestion("Test?"))
            mocked_print.assert_has_calls([mock.call("Test? ", end="")])

    def test_get_input_return(self):
        test_input = "Aaron"
        with mock.patch("builtins.input", return_value=test_input):
            raw_input = Console().get_input()
            self.assertIsInstance(raw_input, str)
            self.assertEqual(raw_input, test_input)

    def test_display_error(self):
        test_error_message = "ERROR MESSAGE"
        with mock.patch("builtins.print") as mock_print:
            console = Console()
            console.display_error(Exception(test_error_message))
            mock_print.assert_called()

    def test_default_string(self):
        cases = [
            DefaultStringTest(PlainQuestion(""), ""),
            DefaultStringTest(PlainQuestion("", "3.10"), "[3.10]"),
            DefaultStringTest(BoolQuestion(""), ""),
            DefaultStringTest(BoolQuestion("", "y"), "[Y]"),
            DefaultStringTest(BoolQuestion("", "n"), "[N]"),
        ]
        display = Console()
        for case in cases:
            self.assertEqual(display.get_default_string(case.question), case.expected)

    def test_display_message(self):
        test_message = "test message"
        with mock.patch("builtins.print") as mock_print:
            console = Console()
            console.display_message(test_message)
            mock_print.assert_called()
