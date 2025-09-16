from enum import Enum


class GetApiV1AccountsNameRatingsRating(str, Enum):
    """GetApiV1AccountsNameRatingsRating enumeration."""

    DISLIKE = "dislike"
    LIKE = "like"

    def __str__(self) -> str:
        return str(self.value)
