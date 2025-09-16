from enum import Enum


class GetApiV1UsersMeSubscriptionsSort(str, Enum):
    """GetApiV1UsersMeSubscriptionsSort enumeration."""

    VALUE_0 = "-id"
    VALUE_1 = "-createdAt"
    VALUE_2 = "-channelUpdatedAt"

    def __str__(self) -> str:
        return str(self.value)
