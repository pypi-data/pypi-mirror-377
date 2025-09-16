from enum import Enum


class SearchVideosSearchTarget(str, Enum):
    """SearchVideosSearchTarget enumeration."""

    LOCAL = "local"
    SEARCH_INDEX = "search-index"

    def __str__(self) -> str:
        return str(self.value)
