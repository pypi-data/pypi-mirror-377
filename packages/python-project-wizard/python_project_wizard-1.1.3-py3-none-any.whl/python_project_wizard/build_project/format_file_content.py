from dataclasses import fields
import re

from python_project_wizard.project import Project
from python_project_wizard.field import get_field_value
from python_project_wizard.build_project.name import source_directory


def format_file_content(content: str, project: Project) -> str:
    content = remove_unnecessary_sections(content, project)
    content = add_project_fields(content, project)
    return content


def remove_unnecessary_sections(content: str, project: Project) -> str:
    for field in fields(project):
        template_pattern = f'"""ppw: {field.name}-(.*?)"""'
        replace_string = r"\1" if get_field_value(project, field.name) else ""
        content = re.sub(template_pattern, replace_string, content, flags=re.DOTALL)
    return content


def add_project_fields(content: str, project: Project) -> str:
    content = re.sub("{project_source}", source_directory(project.name), content)
    content = re.sub("{project_title}", project.name.title(), content)
    return content
