from enum import Enum


class AddWatermarkName(str, Enum):
    """Add watermark operation name."""

    ADD_WATERMARK = "add-watermark"

    def __str__(self) -> str:
        return str(self.value)
