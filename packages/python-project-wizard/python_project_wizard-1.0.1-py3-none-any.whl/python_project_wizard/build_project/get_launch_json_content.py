from typing import Any
from python_project_wizard.project import Project
from python_project_wizard.build_project.name import *
import json


def get_launch_json_content(project: Project) -> None:
    json_object = {
        "version": "0.2.0",
        "configurations": determine_configurations(project),
    }
    return json.dumps(json_object, indent=2)


def determine_configurations(project: Project) -> list[dict[str, Any]]:
    result = [launch_config(project)]
    if project.use_black_formatting:
        result.append(black_formatting_config(project))
    if project.use_unittest:
        result.append(unittest_config())
    return result


def launch_config(project: Project) -> dict[str, Any]:
    return {
        "name": "Launch",
        "type": "python",
        "request": "launch",
        "module": f"{source_directory(project.name)}.main",
        "justMyCode": True,
    }


def black_formatting_config(project: Project) -> dict[str, Any]:
    return {
        "name": "Format",
        "type": "python",
        "request": "launch",
        "module": "black",
        "justMyCode": True,
        "args": [source_directory(project.name)],
    }


def unittest_config() -> dict[str, Any]:
    return {
        "name": "Test",
        "type": "python",
        "request": "launch",
        "module": "unittest",
        "justMyCode": True,
    }
