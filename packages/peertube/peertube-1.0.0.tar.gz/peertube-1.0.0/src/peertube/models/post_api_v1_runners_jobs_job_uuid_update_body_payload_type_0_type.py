from enum import Enum


class PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0Type(str, Enum):
    """PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0Type enumeration."""

    ADD_CHUNK = "add-chunk"
    REMOVE_CHUNK = "remove-chunk"

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.value)
