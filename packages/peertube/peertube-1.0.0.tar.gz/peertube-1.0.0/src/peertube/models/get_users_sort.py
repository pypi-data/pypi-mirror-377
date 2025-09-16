from enum import Enum


class GetUsersSort(str, Enum):
    """GetUsersSort enumeration."""

    VALUE_0 = "-id"
    VALUE_1 = "-username"
    VALUE_2 = "-createdAt"

    def __str__(self) -> str:
        return str(self.value)
