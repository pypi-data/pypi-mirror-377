from enum import Enum


class GetVideosSkipCount(str, Enum):
    """GetVideosSkipCount enumeration."""

    FALSE = "false"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
