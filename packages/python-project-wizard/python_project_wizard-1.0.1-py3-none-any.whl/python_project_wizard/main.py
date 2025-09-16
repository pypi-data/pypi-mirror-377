from python_project_wizard.build_project.build_project import build_project
from python_project_wizard.dialog.sync_dialog import SyncDialog
from python_project_wizard.display.console import Console
from python_project_wizard.display.console_text import ConsoleTextModifier, modify_text
from python_project_wizard.project import Project


def create_main_console():
    shell_prompt = (
        modify_text(
            modify_text("Merlin", ConsoleTextModifier.OKBLUE), ConsoleTextModifier.BOLD
        )
        + "$"
    )
    error_prefix = modify_text(
        modify_text("[ERROR]", ConsoleTextModifier.WARNING), ConsoleTextModifier.BOLD
    )
    message_prefix = modify_text("[INFO]", ConsoleTextModifier.BOLD)
    return Console(shell_prompt, error_prefix, message_prefix)


def main():
    console = create_main_console()
    dialog = SyncDialog[Project](console)
    project = dialog.run(Project())
    build_project(project, console)


if __name__ == "__main__":
    main()
