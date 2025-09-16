from enum import Enum


class JobState(str, Enum):
    """JobState enumeration."""

    ACTIVE = "active"
    COMPLETED = "completed"
    DELAYED = "delayed"
    FAILED = "failed"
    WAITING = "waiting"

    def __str__(self) -> str:
        return str(self.value)
