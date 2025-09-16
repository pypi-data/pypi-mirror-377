import unittest
from dataclasses import dataclass, field

from python_project_wizard.dialog.dialog import Dialog
from python_project_wizard.dialog.sync_dialog import SyncDialog
from python_project_wizard.display.display import Display
from python_project_wizard.exception import DefaultMissingException
from python_project_wizard.field import question_field
from python_project_wizard.project import Project
from python_project_wizard.question.bool_question import BoolQuestion
from python_project_wizard.question.plain_question import PlainQuestion
from python_project_wizard.question.question import Question


@dataclass
class TestDisplay(Display):
    inputs: list[str] = field(default_factory=list)
    errors: list[Exception] = field(init=False, default_factory=list)
    index: int = field(init=False, default=0)

    def prompt(self, question: Question) -> None:
        return

    def get_input(self) -> str:
        result = self.inputs[self.index]
        self.index += 1
        return result

    def display_error(self, exception: Exception) -> None:
        self.errors.append(exception)

    def display_message(self, message: str) -> None:
        return


@dataclass
class TestProject:
    name: str = question_field(PlainQuestion("Name?"))
    python_version: str = question_field(PlainQuestion("Version?"))
    use_black_formatting: bool = question_field(BoolQuestion("Black?"))
    use_logging: bool = question_field(BoolQuestion("Logging?"))
    use_unittest: bool = question_field(BoolQuestion("Unit Tests?"))
    use_configs: bool = question_field(BoolQuestion("Configs?", "Y"))
    use_args: bool = question_field(BoolQuestion("Arguments?", "N"))


class SyncDialogTestSuite(unittest.TestCase):
    def test_constructor(self):
        self.assertIsInstance(SyncDialog[Project](TestDisplay()), Dialog)

    def test_run(self):
        test_inputs = [
            "Merlin",  # Name
            "3.10",  # Version
            "Y",  # Black formatting
            "Y",  # Logging
            "N",  # Unit test
            "Y",  # Configs
            "Y",  # args
        ]
        dialog = SyncDialog[Project](TestDisplay(test_inputs))
        project = dialog.run(Project())
        self.assertEqual(project.name, "Merlin")
        self.assertEqual(project.python_version, "3.10")
        self.assertEqual(project.use_black_formatting, True)
        self.assertEqual(project.use_logging, True)
        self.assertEqual(project.use_unittest, False)
        self.assertEqual(project.use_configs, True)
        self.assertEqual(project.use_args, True)

    def test_get_answer_validator_return_value(self):
        test_input = "Yes"
        dialog = SyncDialog[bool](TestDisplay([test_input]))
        answer = dialog.prompt_user_until_answer_provided(
            BoolQuestion("Do you use VSCode?")
        )
        self.assertIsInstance(answer.value, bool)
        self.assertTrue(answer.value)

    def test_get_answer_two_prompts_on_error(self):
        test_inputs = ["huh", "N"]
        dialog = SyncDialog[bool](TestDisplay(test_inputs))
        answer = dialog.prompt_user_until_answer_provided(
            BoolQuestion("Do you use VSCode?")
        )
        self.assertIsInstance(answer.value, bool)
        self.assertFalse(answer.value)

    def test_error_on_blank_with_no_default(self):
        test_inputs = ["", "Merlin"]
        dialog = SyncDialog[str](TestDisplay(test_inputs))
        answer = dialog.prompt_user_until_answer_provided(PlainQuestion("Name?"))
        self.assertIsInstance(answer.value, str)
        self.assertEqual(answer.value, "Merlin")

    def test_exceptions_displayed(self):
        test_inputs = [
            "",
            "Merlin",  # Name
            "3.10",  # Version
            "",
            "Y",  # Black formatting
            "huh",
            "Y",  # Logging
            "N",  # Unit test
            "",  # Configs
            "",  # args
        ]
        expected_errors = [DefaultMissingException, DefaultMissingException, ValueError]
        display = TestDisplay(test_inputs)
        dialog = SyncDialog[TestProject](display)
        dialog.run(TestProject())
        self.assertEqual(len(expected_errors), len(display.errors))
        for i in range(len(expected_errors)):
            self.assertIsInstance(display.errors[i], expected_errors[i])
