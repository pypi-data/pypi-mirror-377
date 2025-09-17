import re

from python_project_wizard.answer import Answer
from python_project_wizard.question.question import Question


class BoolQuestion(Question):
    def validate_input_or_default(self, raw_input: str) -> Answer:
        if re.match("^y", raw_input, re.IGNORECASE):
            return Answer(True)
        if re.match("^n", raw_input, re.IGNORECASE):
            return Answer(False)
        raise ValueError(f"Unexpected value received: `{raw_input}`.")
