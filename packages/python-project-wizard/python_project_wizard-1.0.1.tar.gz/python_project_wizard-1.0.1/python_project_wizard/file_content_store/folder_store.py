import os

from dataclasses import dataclass

from python_project_wizard.file_content_store.file_content_store import FileContentStore


@dataclass
class FolderStore(FileContentStore):
    templates_directory_path: str = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "templates"
    )

    def get_file_content(self) -> dict[str, str]:
        self.validate_directory_path()
        template_files = self.get_template_files()
        return self.get_file_contents(template_files)

    def validate_directory_path(self) -> None:
        if not os.path.exists(self.templates_directory_path):
            raise InvalidDirectory()
        if not os.path.isdir(self.templates_directory_path):
            raise InvalidDirectory()

    def get_template_files(self) -> list[str]:
        return [
            full_path
            for file in os.listdir(self.templates_directory_path)
            if os.path.isfile(
                full_path := os.path.join(self.templates_directory_path, file)
            )
        ]

    def get_file_contents(self, template_files: list[str]) -> dict[str, str]:
        file_contents = {}
        for template_file in template_files:
            file_content = self.get_template_file_content(template_file)
            file_name = os.path.basename(template_file)
            file_contents[file_name] = file_content
        return file_contents

    def get_template_file_content(self, template_file: str) -> str:
        with open(template_file) as file:
            return file.read()


class InvalidDirectory(Exception):
    ...
