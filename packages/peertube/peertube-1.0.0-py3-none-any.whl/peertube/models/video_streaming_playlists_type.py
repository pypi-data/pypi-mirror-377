from enum import IntEnum


class VideoStreamingPlaylistsType(IntEnum):
    """VideoStreamingPlaylistsType enumeration."""

    VALUE_1 = 1

    def __str__(self) -> str:
        return str(self.value)
