from enum import Enum


class PutApiV1VideosIdRateBodyRating(str, Enum):
    """PutApiV1VideosIdRateBodyRating enumeration."""

    DISLIKE = "dislike"
    LIKE = "like"

    def __str__(self) -> str:
        return str(self.value)
