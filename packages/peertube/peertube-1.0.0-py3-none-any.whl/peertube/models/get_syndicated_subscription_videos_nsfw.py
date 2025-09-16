from enum import Enum


class GetSyndicatedSubscriptionVideosNsfw(str, Enum):
    """GetSyndicatedSubscriptionVideosNsfw enumeration."""

    FALSE = "false"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
