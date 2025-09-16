import os
import unittest
import unittest.mock as mock
from typing import Any

from dataclasses import dataclass, field
from python_project_wizard.build_project.build_files import *
from python_project_wizard.project import Project
from python_project_wizard.build_project.get_launch_json_content import *
from python_project_wizard.file import File
from python_project_wizard.file_content_store.file_content_store import FileContentStore
from python_project_wizard.build_project.file_builder import FileBuilder
from python_project_wizard.display.display import Display
from python_project_wizard.question.question import Question


@dataclass
class TestDisplay(Display):
    def prompt(self, question: Question) -> None:
        return

    def get_input(self) -> str:
        return ""

    def display_error(self, exception: Exception) -> None:
        return

    def display_message(self, message: str) -> None:
        return


@dataclass
class TestStore(FileContentStore):
    test_files: dict[str, str]

    def get_file_content(self) -> dict[str, str]:
        return self.test_files


def unordered_equal(seq1: list[Any], seq2: list[Any]) -> bool:
    for item in seq1:
        if item not in seq2:
            return False
    for item in seq2:
        if item not in seq1:
            return False
    return True


@dataclass
class TestBuilder:
    calls: list[File] = field(default_factory=list)

    def build(self, file: File):
        self.calls.append(file)


class BuildFilesTestSuite(unittest.TestCase):
    @mock.patch("python_project_wizard.build_project.build_files.build_files")
    @mock.patch(
        "python_project_wizard.build_project.build_files.get_files", return_value=[]
    )
    def test_get_and_build_files(
        self, mocked_get_files: mock.Mock, mocked_build_files: mock.Mock
    ):
        project = Project(name="merlin project")
        directories = Directories(project)
        get_and_build_files(project, directories, TestDisplay())
        mocked_get_files.assert_called_once_with(project)
        mocked_build_files.assert_called_once_with(
            [], FileBuilder(directories), TestDisplay()
        )

    @mock.patch("python_project_wizard.build_project.build_files.get_files_from_store")
    @mock.patch("python_project_wizard.build_project.build_files.get_launch_json")
    @mock.patch("python_project_wizard.build_project.build_files.get_static_files")
    def test_get_files(
        self,
        mocked_static_files: mock.Mock,
        mocked_launch_file: mock.Mock,
        mocked_files_from_store: mock.Mock,
    ):
        project = Project(name="merlin project")
        get_files(project)
        mocked_static_files.assert_called_once_with(project)
        mocked_launch_file.assert_called_once_with(project)
        mocked_files_from_store.assert_called_once_with(project, FolderStore())

    def test_get_static(self):
        project = Project(name="merlin project")
        static_files = get_static_files(project)
        self.assertEqual(
            static_files,
            [
                File(
                    filename="README.md",
                    content="# Merlin Project",
                    destination=Destination.MAIN,
                ),
                File(
                    filename="__init__.py", content="", destination=Destination.SOURCE
                ),
            ],
        )

    def test_get_launch_json(self):
        project = Project(name="merlin project")
        launch_file_content = """{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Launch",
      "type": "python",
      "request": "launch",
      "module": "merlin_project.main",
      "justMyCode": true
    }
  ]
}"""
        expected_file = File(
            filename="launch.json",
            content=launch_file_content,
            destination=Destination.VS_CODE,
        )
        launch_file = get_launch_json(project)
        self.assertEqual(launch_file, expected_file)

    def test_get_source_files(self):
        project = Project(name="merlin project")
        content = """# Hello World
def main():
    ...

if __name__ == '__main__':
    main()
"""
        test_files = {"main.py": content}
        store = TestStore(test_files)
        files = get_files_from_store(project, store)
        self.assertEqual(
            files,
            [File(filename="main.py", content=content, destination=Destination.SOURCE)],
        )

    def test_get_main_directory_files(self):
        project = Project(name="merlin project", use_configs=True, use_unittest=True)
        test_files = {
            "main.py": "# Main file",
            "configs.json": "{}",
            "configs.py": "# Configs file",
            "__init__.py": "",
            "test_example.py": "# Test Example",
        }
        store = TestStore(test_files)
        files = get_files_from_store(project, store)
        self.assertTrue(
            unordered_equal(
                files,
                [
                    File(
                        filename="main.py",
                        content="# Main file",
                        destination=Destination.SOURCE,
                    ),
                    File(
                        filename="configs.json",
                        content="{}",
                        destination=Destination.MAIN,
                    ),
                    File(
                        filename="configs.py",
                        content="# Configs file",
                        destination=Destination.SOURCE,
                    ),
                    File(
                        filename="__init__.py", content="", destination=Destination.TEST
                    ),
                    File(
                        filename="test_example.py",
                        content="# Test Example",
                        destination=Destination.TEST,
                    ),
                ],
            )
        )

    def test_get_main_directory_files_with_cleaning(self):
        project = Project(name="merlin project", use_configs=True)
        test_files = {
            "main.py": '''"""ppw: use_args-from args import get_argparser
""""""ppw: use_configs-from configs import load_configs
""""""ppw: use_logging-from log import enable_logging
import logging
"""''',
            "configs.json": "{}",
            "configs.py": "# Configs file",
        }
        store = TestStore(test_files)
        files = get_files_from_store(project, store)
        self.assertTrue(
            unordered_equal(
                files,
                [
                    File(
                        filename="main.py",
                        content="""from configs import load_configs
""",
                        destination=Destination.SOURCE,
                    ),
                    File(
                        filename="configs.json",
                        content="{}",
                        destination=Destination.MAIN,
                    ),
                    File(
                        filename="configs.py",
                        content="# Configs file",
                        destination=Destination.SOURCE,
                    ),
                ],
            )
        )

    def test_build_files(self):
        files = [
            File(
                filename="main.py",
                content="# Main file",
                destination=Destination.SOURCE,
            ),
            File(filename="configs.json", content="{}", destination=Destination.MAIN),
            File(
                filename="configs.py",
                content="# Configs file",
                destination=Destination.SOURCE,
            ),
        ]
        builder = TestBuilder()
        build_files(files, builder, TestDisplay())
        self.assertTrue(unordered_equal(builder.calls, files))
