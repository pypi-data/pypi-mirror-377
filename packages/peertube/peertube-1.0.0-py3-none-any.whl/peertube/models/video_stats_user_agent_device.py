from enum import Enum


class VideoStatsUserAgentDevice(str, Enum):
    """VideoStatsUserAgentDevice class."""

    CONSOLE = "console"
    DESKTOP = "desktop"
    EMBEDDED = "embedded"
    MOBILE = "mobile"
    SMARTTV = "smarttv"
    TABLET = "tablet"
    WEARABLE = "wearable"
    XR = "xr"

    def __str__(self) -> str:
        return str(self.value)
