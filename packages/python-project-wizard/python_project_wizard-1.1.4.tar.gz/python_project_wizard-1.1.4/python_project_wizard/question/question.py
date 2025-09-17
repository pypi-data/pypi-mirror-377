from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from python_project_wizard.answer import Answer
from python_project_wizard.exception import DefaultMissingException


@dataclass
class Question(ABC):
    prompt: str
    default: Optional[str] = field(default=None)

    def __post_init__(self):
        if self.default is None:
            return
        self.validate_input_or_default(self.default)

    def validate_raw_input(self, raw_input: str) -> Answer:
        input = self.check_for_default(raw_input)
        return self.validate_input_or_default(input)

    @abstractmethod
    def validate_input_or_default(self, input: str) -> Answer:
        ...

    def check_for_default(self, raw_input: str) -> str:
        if raw_input == "":
            return self.apply_default()
        return raw_input

    def apply_default(self) -> str:
        if self.default is None:
            raise DefaultMissingException("Please enter a value")
        return self.default
