from enum import Enum


class GetJobsState(str, Enum):
    """GetJobsState enumeration."""

    ACTIVE = "active"
    COMPLETED = "completed"
    DELAYED = "delayed"
    FAILED = "failed"
    VALUE_0 = ""
    WAITING = "waiting"

    def __str__(self) -> str:
        return str(self.value)
