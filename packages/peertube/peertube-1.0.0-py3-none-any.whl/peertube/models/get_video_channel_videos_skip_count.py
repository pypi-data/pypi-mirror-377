from enum import Enum


class GetVideoChannelVideosSkipCount(str, Enum):
    """GetVideoChannelVideosSkipCount enumeration."""

    FALSE = "false"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
