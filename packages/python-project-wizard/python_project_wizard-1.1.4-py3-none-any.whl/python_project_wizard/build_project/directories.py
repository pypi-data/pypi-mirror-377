import os

from python_project_wizard.project import Project
from python_project_wizard.build_project.name import *


class Directories:
    def __init__(self, project: Project):
        cwd = os.getcwd()
        self.main = os.path.join(cwd, main_directory(project.name))
        self.source = os.path.join(self.main, source_directory(project.name))
        self.dot_vscode = os.path.join(self.main, ".vscode")
        self.test = os.path.join(self.source, "test")
