from enum import Enum


class FileRedundancyInformationStrategy(str, Enum):
    """FileRedundancyInformationStrategy enumeration."""

    MANUAL = "manual"
    MOST_VIEWS = "most-views"
    RECENTLY_ADDED = "recently-added"
    TRENDING = "trending"

    def __str__(self) -> str:
        return str(self.value)
