from enum import Enum


class StrEnum(str, Enum):
    pass


# Based on: https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
class ConsoleTextModifier(StrEnum):
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def modify_text(message: str, modifier: ConsoleTextModifier):
    return f"{modifier.value}{message}{ConsoleTextModifier.END.value}"
