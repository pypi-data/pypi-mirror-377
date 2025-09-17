from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import ClassVar


class Destination(Enum):
    MAIN = auto()
    SOURCE = auto()
    VS_CODE = auto()
    TEST = auto()
    INVALID = auto()


@dataclass
class File:
    INVALID_FILENAME: ClassVar[str] = "<INVALID_FILENAME>"
    filename: str = INVALID_FILENAME
    content: str = ""
    destination: Destination = Destination.INVALID

    def is_valid(self) -> bool:
        return (
            self.filename != File.INVALID_FILENAME
            and self.destination is not Destination.INVALID
        )
