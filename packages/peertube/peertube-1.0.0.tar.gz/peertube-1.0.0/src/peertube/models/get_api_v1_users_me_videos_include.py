from enum import IntEnum


class GetApiV1UsersMeVideosInclude(IntEnum):
    """GetApiV1UsersMeVideosInclude enumeration."""

    VALUE_0 = 0
    VALUE_1 = 1
    VALUE_2 = 2
    VALUE_4 = 4
    VALUE_8 = 8
    VALUE_16 = 16
    VALUE_32 = 32

    def __str__(self) -> str:
        return str(self.value)
