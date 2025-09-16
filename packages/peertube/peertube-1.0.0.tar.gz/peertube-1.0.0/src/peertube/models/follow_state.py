from enum import Enum


class FollowState(str, Enum):
    """FollowState enumeration."""

    ACCEPTED = "accepted"
    PENDING = "pending"

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.value)
