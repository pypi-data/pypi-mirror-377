from enum import Enum


class GetApiV1UsersMeSubscriptionsVideosSkipCount(str, Enum):
    """GetApiV1UsersMeSubscriptionsVideosSkipCount enumeration."""

    FALSE = "false"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
