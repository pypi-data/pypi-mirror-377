from enum import Enum


class AddIntroName(str, Enum):
    """Add intro operation name."""

    ADD_INTRO = "add-intro"

    def __str__(self) -> str:
        return str(self.value)
