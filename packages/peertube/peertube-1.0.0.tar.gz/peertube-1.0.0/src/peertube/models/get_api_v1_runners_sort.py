from enum import Enum


class GetApiV1RunnersSort(str, Enum):
    """GetApiV1RunnersSort enumeration."""

    CREATEDAT = "createdAt"

    def __str__(self) -> str:
        return str(self.value)
