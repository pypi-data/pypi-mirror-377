from dataclasses import dataclass

from python_project_wizard.display.display import Display
from python_project_wizard.question.question import Question


@dataclass
class Console(Display):
    shell_prompt: str = ""
    error_prefix: str = ""
    message_prefix: str = ""

    def prompt(self, question: Question) -> None:
        default_string = self.get_default_string(question)
        question_string = f"{self.shell_prompt} {question.prompt}{f' {default_string}'}"
        question_string = question_string.strip()
        return print(f"{question_string} ", end="")

    def get_default_string(self, question: Question) -> str:
        return f"[{question.default.upper()}]" if question.default is not None else ""

    def get_input(self) -> str:
        return input()

    def display_error(self, exception: Exception) -> None:
        print(f"{self.error_prefix} {str(exception)}")

    def display_message(self, message: str) -> None:
        print(f"{self.message_prefix} {message}")
