from enum import Enum


class GetApiV1UsersMeVideosSort(str, Enum):
    """GetApiV1UsersMeVideosSort enumeration."""

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
        return str(self.value)
