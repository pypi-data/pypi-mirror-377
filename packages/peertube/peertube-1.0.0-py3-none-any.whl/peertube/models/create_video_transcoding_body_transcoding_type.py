from enum import Enum


class CreateVideoTranscodingBodyTranscodingType(str, Enum):
    """CreateVideoTranscodingBodyTranscodingType enumeration."""

    HLS = "hls"
    WEB_VIDEO = "web-video"

    def __str__(self) -> str:
        return str(self.value)
