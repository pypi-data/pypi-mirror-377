from enum import Enum


class GetMirroredVideosTarget(str, Enum):
    """GetMirroredVideosTarget enumeration."""

    MY_VIDEOS = "my-videos"
    REMOTE_VIDEOS = "remote-videos"

    def __str__(self) -> str:
        return str(self.value)
