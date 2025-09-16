import subprocess

from dataclasses import fields
from python_project_wizard.field import get_field_value
from python_project_wizard.build_project.directories import Directories
from python_project_wizard.project import Project


def create_pipenv(project: Project, directories: Directories) -> None:
    initialize_pipenv(project, directories)
    install_packages(project, directories)


def initialize_pipenv(project: Project, directories: Directories) -> None:
    subprocess.run(
        ["pipenv", "install", "--python", project.python_version], cwd=directories.main
    )


def install_packages(project: Project, directories: Directories) -> None:
    for field in fields(project):
        field_value = get_field_value(project, field.name)
        if field_value and field.metadata["package"] is not None:
            install_package(directories.main, field.metadata["package"])


def install_package(cwd: str, package: str) -> None:
    subprocess.run(["pipenv", "install", "-d", package], cwd=cwd)
