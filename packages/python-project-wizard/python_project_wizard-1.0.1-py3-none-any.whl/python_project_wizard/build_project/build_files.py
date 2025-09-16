import os
from dataclasses import fields, Field

from python_project_wizard.build_project.directories import Directories
from python_project_wizard.build_project.get_launch_json_content import (
    get_launch_json_content,
)
from python_project_wizard.field import get_field_value
from python_project_wizard.file_content_store.file_content_store import FileContentStore
from python_project_wizard.file_content_store.folder_store import FolderStore
from python_project_wizard.project import Project
from python_project_wizard.file import File, Destination
from python_project_wizard.build_project.file_builder import FileBuilder
from python_project_wizard.build_project.clean_main_content import clean_main_content
from python_project_wizard.display.display import Display


def get_and_build_files(
    project: Project, directories: Directories, display: Display
) -> None:
    files = get_files(project)
    build_files(files, FileBuilder(directories), display)


def get_files(project: Project) -> list[File]:
    files = get_static_files(project)
    files.append(get_launch_json(project))
    files += get_files_from_store(project, FolderStore())
    return files


def get_static_files(project: Project) -> list[File]:
    return [
        File(
            filename="README.md",
            content=f"# {project.name.title()}",
            destination=Destination.MAIN,
        ),
        File(filename="__init__.py", content="", destination=Destination.SOURCE),
    ]


def get_launch_json(project: Project) -> File:
    return File(
        filename="launch.json",
        content=get_launch_json_content(project),
        destination=Destination.VS_CODE,
    )


def get_files_from_store(project: Project, store: FileContentStore) -> list[File]:
    stored_file_content = store.get_file_content()
    requested_files = get_requested_files(project)
    for file in requested_files:
        file.content = stored_file_content[file.filename]
        if file.filename == "main.py":
            file.content = clean_main_content(file.content, project)
    return requested_files


def get_requested_files(project: Project) -> list[File]:
    result = []
    for field in fields(project):
        if get_field_value(project, field.name):
            result += field.metadata["files"]
    return result


def build_files(files: list[File], builder: FileBuilder, display: Display) -> None:
    for file in files:
        display.display_message(f"Building file: {file.filename}")
        builder.build(file)
