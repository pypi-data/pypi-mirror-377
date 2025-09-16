from enum import Enum


class GetAccountVideosSort(str, Enum):
    """GetAccountVideosSort enumeration."""

    NAME = "name"
    VALUE_1 = "-duration"
    VALUE_2 = "-createdAt"
    VALUE_3 = "-publishedAt"
    VALUE_4 = "-views"
    VALUE_5 = "-likes"
    VALUE_6 = "-comments"
    VALUE_7 = "-trending"
    VALUE_8 = "-hot"
    VALUE_9 = "-best"

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.value)
