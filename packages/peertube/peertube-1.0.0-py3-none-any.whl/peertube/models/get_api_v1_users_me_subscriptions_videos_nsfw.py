from enum import Enum


class GetApiV1UsersMeSubscriptionsVideosNsfw(str, Enum):
    """GetApiV1UsersMeSubscriptionsVideosNsfw enumeration."""

    FALSE = "false"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
