from enum import Enum


class GetApiV1UsersMeVideosSkipCount(str, Enum):
    """GetApiV1UsersMeVideosSkipCount enumeration."""

    FALSE = "false"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
