from enum import Enum


class GetSyndicatedVideosFormat(str, Enum):
    """GetSyndicatedVideosFormat enumeration."""

    ATOM = "atom"
    ATOM1 = "atom1"
    JSON = "json"
    JSON1 = "json1"
    RSS = "rss"
    RSS2 = "rss2"
    XML = "xml"

    def __str__(self) -> str:
        return str(self.value)
