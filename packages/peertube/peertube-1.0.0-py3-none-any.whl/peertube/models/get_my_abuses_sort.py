from enum import Enum


class GetMyAbusesSort(str, Enum):
    """GetMyAbusesSort enumeration."""

    VALUE_0 = "-id"
    VALUE_1 = "-createdAt"
    VALUE_2 = "-state"

    def __str__(self) -> str:
        return str(self.value)
