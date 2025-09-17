from python_project_wizard.answer import Answer
from python_project_wizard.question.question import Question


class TextQuestion(Question):
    def validate_input_or_default(self, raw_input: str) -> Answer:
        return Answer(raw_input)
