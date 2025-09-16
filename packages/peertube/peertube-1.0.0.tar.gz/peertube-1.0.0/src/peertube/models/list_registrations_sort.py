from enum import Enum


class ListRegistrationsSort(str, Enum):
    """ListRegistrationsSort enumeration."""

    CREATEDAT = "createdAt"
    STATE = "state"
    VALUE_0 = "-createdAt"
    VALUE_3 = "-state"

    def __str__(self) -> str:
        return str(self.value)
