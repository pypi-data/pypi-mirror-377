from abc import ABC, abstractmethod

from python_project_wizard.question.question import Question


class Display(ABC):
    @abstractmethod
    def prompt(self, question: Question) -> None:
        ...

    @abstractmethod
    def get_input(self) -> str:
        ...

    @abstractmethod
    def display_error(self, exception: Exception) -> None:
        ...

    @abstractmethod
    def display_message(self, message: str) -> None:
        ...
