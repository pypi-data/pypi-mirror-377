from enum import Enum


class GetAccountVideosNsfw(str, Enum):
    """GetAccountVideosNsfw enumeration."""

    FALSE = "false"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
