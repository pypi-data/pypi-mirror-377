from enum import Enum


class SearchVideosNsfw(str, Enum):
    """SearchVideosNsfw enumeration."""

    FALSE = "false"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
