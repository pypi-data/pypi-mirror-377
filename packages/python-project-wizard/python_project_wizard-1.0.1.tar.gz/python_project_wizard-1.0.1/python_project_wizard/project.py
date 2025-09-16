from python_project_wizard.question.plain_question import PlainQuestion
from python_project_wizard.question.bool_question import BoolQuestion
from python_project_wizard.question.version_question import VersionQuestion
from python_project_wizard.field import question_field
from python_project_wizard.file import Destination, File

from dataclasses import dataclass


@dataclass
class Project:
    name: str = question_field(
        PlainQuestion("What is the name of your Project?"),
        files=[File(filename="main.py", destination=Destination.SOURCE)],
    )
    python_version: str = question_field(
        VersionQuestion("What version of Python?", default="3.10"),
    )
    use_black_formatting: bool = question_field(
        BoolQuestion("Add Black formatting?", default="Y"),
        package="black",
    )
    use_logging: bool = question_field(
        BoolQuestion("Add logging?", default="Y"),
        files=[
            File(filename="log.py", destination=Destination.SOURCE),
            File(filename="logging.conf", destination=Destination.MAIN),
        ],
    )
    use_unittest: bool = question_field(
        BoolQuestion("Add Unit Tests?", default="Y"),
        files=[
            File(filename="__init__.py", destination=Destination.TEST),
            File(filename="test_example.py", destination=Destination.TEST),
        ],
    )
    use_configs: bool = question_field(
        BoolQuestion("Add configs?", default="Y"),
        files=[
            File(filename="configs.py", destination=Destination.SOURCE),
            File(filename="configs.json", destination=Destination.MAIN),
        ],
    )
    use_args: bool = question_field(
        BoolQuestion("Add arguments?", default="N"),
        files=[File(filename="args.py", destination=Destination.SOURCE)],
    )
