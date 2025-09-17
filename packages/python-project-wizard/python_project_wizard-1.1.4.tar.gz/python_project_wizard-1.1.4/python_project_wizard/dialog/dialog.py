from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from python_project_wizard.display.display import Display

T = TypeVar("T")


@dataclass
class Dialog(ABC, Generic[T]):
    display: Display

    @abstractmethod
    def run(self, result: T) -> T:
        ...
