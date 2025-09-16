from enum import Enum


class GetVideosNsfw(str, Enum):
    """GetVideosNsfw enumeration."""

    FALSE = "false"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
