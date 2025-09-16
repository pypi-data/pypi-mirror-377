from enum import Enum


class GetAbusesFilter(str, Enum):
    """GetAbusesFilter enumeration."""

    ACCOUNT = "account"
    COMMENT = "comment"
    VIDEO = "video"

    def __str__(self) -> str:
        return str(self.value)
