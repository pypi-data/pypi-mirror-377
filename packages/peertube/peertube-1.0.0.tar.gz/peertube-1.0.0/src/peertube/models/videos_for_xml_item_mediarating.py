from enum import Enum


class VideosForXMLItemMediarating(str, Enum):
    """VideosForXMLItemMediarating class."""

    ADULT = "adult"
    NONADULT = "nonadult"

    def __str__(self) -> str:
        return str(self.value)
