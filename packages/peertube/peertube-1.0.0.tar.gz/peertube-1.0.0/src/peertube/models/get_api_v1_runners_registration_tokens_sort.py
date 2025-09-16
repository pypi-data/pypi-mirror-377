from enum import Enum


class GetApiV1RunnersRegistrationTokensSort(str, Enum):
    """GetApiV1RunnersRegistrationTokensSort enumeration."""

    CREATEDAT = "createdAt"

    def __str__(self) -> str:
        return str(self.value)
