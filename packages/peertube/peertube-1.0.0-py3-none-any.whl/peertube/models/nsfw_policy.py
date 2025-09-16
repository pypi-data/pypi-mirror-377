from enum import Enum


class NSFWPolicy(str, Enum):
    """NSFWPolicy class."""

    DISPLAY = "display"
    DO_NOT_LIST = "do_not_list"
    WARN = "warn"

    def __str__(self) -> str:
        return str(self.value)
