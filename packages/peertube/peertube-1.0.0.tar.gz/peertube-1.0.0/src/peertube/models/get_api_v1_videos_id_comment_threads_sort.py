from enum import Enum


class GetApiV1VideosIdCommentThreadsSort(str, Enum):
    """GetApiV1VideosIdCommentThreadsSort enumeration."""

    VALUE_0 = "-createdAt"
    VALUE_1 = "-totalReplies"

    def __str__(self) -> str:
        return str(self.value)
