from enum import Enum


class GetMirroredVideosSort(str, Enum):
    """GetMirroredVideosSort enumeration."""

    NAME = "name"

    def __str__(self) -> str:
        return str(self.value)
