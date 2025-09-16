from enum import IntEnum


class FileStorage(IntEnum):
    """FileStorage enumeration."""

    VALUE_0 = 0
    VALUE_1 = 1

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.value)
