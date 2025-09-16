from enum import Enum


class GetAbusesSort(str, Enum):
    """GetAbusesSort enumeration."""

    VALUE_0 = "-id"
    VALUE_1 = "-createdAt"
    VALUE_2 = "-state"

    def __str__(self) -> str:
        return str(self.value)
