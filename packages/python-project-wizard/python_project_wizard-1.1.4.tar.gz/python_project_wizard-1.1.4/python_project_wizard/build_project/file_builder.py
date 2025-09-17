from dataclasses import dataclass
import os

from python_project_wizard.build_project.directories import Directories
from python_project_wizard.file import File, Destination


@dataclass
class FileBuilder:
    directories: Directories

    def build(self, file: File) -> None:
        if not file.is_valid():
            raise Exception("File cannot be built")
        self.build_parent_directories(file)
        with open(self.resolve_file_path(file), "w+") as built_file:
            built_file.write(file.content)

    def build_parent_directories(self, file: File) -> None:
        os.makedirs(self.resolve_file_directory(file), exist_ok=True)

    def resolve_file_path(self, file: File) -> str:
        return os.path.join(self.resolve_file_directory(file), file.filename)

    def resolve_file_directory(self, file: File) -> str:
        directory = self.directories.main
        if file.destination is Destination.SOURCE:
            directory = self.directories.source
        elif file.destination is Destination.VS_CODE:
            directory = self.directories.dot_vscode
        elif file.destination is Destination.TEST:
            directory = self.directories.test
        return directory
