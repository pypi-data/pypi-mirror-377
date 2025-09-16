from enum import IntEnum


class VideoCommentsPolicySet(IntEnum):
    """VideoCommentsPolicySet enumeration."""

    VALUE_1 = 1
    VALUE_2 = 2
    VALUE_3 = 3

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.value)
