from enum import Enum


class SearchVideosSkipCount(str, Enum):
    """SearchVideosSkipCount enumeration."""

    FALSE = "false"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
