from dataclasses import fields
from typing import Generic, TypeVar

from python_project_wizard.answer import Answer
from python_project_wizard.dialog.dialog import Dialog
from python_project_wizard.field import set_field
from python_project_wizard.question.question import Question

T = TypeVar("T")


class SyncDialog(Dialog, Generic[T]):
    def run(self, result: T) -> T:
        for field in fields(result):
            answer = self.prompt_user_until_answer_provided(field.metadata["question"])
            result = set_field(result, field.name, answer.value)
        return result

    def prompt_user_until_answer_provided(self, question: Question) -> Answer:
        answer = None
        while answer is None:
            answer = self.try_to_get_answer(question)
        return answer

    def try_to_get_answer(self, question: Question) -> Answer:
        try:
            return self.get_input_from_user(question)
        except Exception as e:
            self.display.display_error(e)
            return None

    def get_input_from_user(self, question: Question) -> Answer:
        self.display.prompt(question)
        raw_input = self.display.get_input()
        return question.validate_raw_input(raw_input)
