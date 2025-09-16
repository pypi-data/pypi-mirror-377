from enum import Enum


class GetAccountVideosSkipCount(str, Enum):
    """GetAccountVideosSkipCount enumeration."""

    FALSE = "false"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
