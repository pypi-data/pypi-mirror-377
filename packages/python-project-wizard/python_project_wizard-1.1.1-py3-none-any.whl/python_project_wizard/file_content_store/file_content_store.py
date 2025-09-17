from dataclasses import dataclass
from abc import ABC, abstractmethod

from python_project_wizard.file import File


@dataclass
class FileContentStore(ABC):
    @abstractmethod
    def get_file_content(self) -> dict[str, File]:
        ...
