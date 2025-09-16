from enum import Enum


class ServerConfigCustomTranscodingProfile(str, Enum):
    """ServerConfigCustomTranscodingProfile class."""

    DEFAULT = "default"

    def __str__(self) -> str:
        return str(self.value)
