from enum import Enum


class UserViewingVideoViewEvent(str, Enum):
    """UserViewingVideoViewEvent class."""

    SEEK = "seek"

    def __str__(self) -> str:
        return str(self.value)
