from enum import Enum


class GetApiV1ServerFollowingState(str, Enum):
    """GetApiV1ServerFollowingState enumeration."""

    ACCEPTED = "accepted"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
