from enum import Enum


class CutName(str, Enum):
    """Cut operation name."""

    CUT = "cut"

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.value)
