from enum import Enum


class VideoRatingRating(str, Enum):
    """VideoRatingRating class."""

    DISLIKE = "dislike"
    LIKE = "like"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
