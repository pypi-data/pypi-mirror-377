from enum import IntEnum


class UserRole(IntEnum):
    """UserRole class."""

    ADMIN = 0
    MODERATOR = 1
    USER = 2

    def __str__(self) -> str:
        return str(self.value)
