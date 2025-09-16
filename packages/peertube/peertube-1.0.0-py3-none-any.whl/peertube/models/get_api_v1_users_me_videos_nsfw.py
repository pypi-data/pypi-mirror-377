from enum import Enum


class GetApiV1UsersMeVideosNsfw(str, Enum):
    """GetApiV1UsersMeVideosNsfw enumeration."""

    FALSE = "false"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
