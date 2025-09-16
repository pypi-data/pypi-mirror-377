from enum import Enum


class GetApiV1ServerFollowersActorType(str, Enum):
    """GetApiV1ServerFollowersActorType enumeration."""

    APPLICATION = "Application"
    GROUP = "Group"
    ORGANIZATION = "Organization"
    PERSON = "Person"
    SERVICE = "Service"

    def __str__(self) -> str:
        return str(self.value)
