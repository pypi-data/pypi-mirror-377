from enum import Enum


class GetVideoChannelFollowersSort(str, Enum):
    """GetVideoChannelFollowersSort enumeration."""

    CREATEDAT = "createdAt"

    def __str__(self) -> str:
        return str(self.value)
