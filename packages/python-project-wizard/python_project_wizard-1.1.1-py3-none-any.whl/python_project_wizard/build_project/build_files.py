import os
from dataclasses import fields, Field

from python_project_wizard.build_project.directories import Directories
from python_project_wizard.field import get_field_value
from python_project_wizard.file_content_store.file_content_store import FileContentStore
from python_project_wizard.file_content_store.folder_store import FolderStore
from python_project_wizard.project import Project
from python_project_wizard.file import File, Destination
from python_project_wizard.build_project.file_builder import FileBuilder
from python_project_wizard.build_project.format_file_content import format_file_content
from python_project_wizard.display.display import Display


def get_and_build_files(
    project: Project, directories: Directories, display: Display
) -> None:
    files = get_files_from_store(project, FolderStore())
    build_files(files, FileBuilder(directories), display)


def get_files_from_store(project: Project, store: FileContentStore) -> list[File]:
    stored_file_content = store.get_file_content()
    requested_files = get_requested_files(project)
    for file in requested_files:
        file.content = stored_file_content[file.filename]
        file.content = format_file_content(file.content, project)
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
