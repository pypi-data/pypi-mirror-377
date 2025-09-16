from enum import Enum


class GetVideoBlocksSort(str, Enum):
    """GetVideoBlocksSort enumeration."""

    NAME = "name"
    VALUE_0 = "-id"
    VALUE_2 = "-duration"
    VALUE_3 = "-views"
    VALUE_4 = "-likes"
    VALUE_5 = "-dislikes"
    VALUE_6 = "-uuid"
    VALUE_7 = "-createdAt"

    def __str__(self) -> str:
        return str(self.value)
