from enum import Enum


class PlaybackMetricCreatePlayerMode(str, Enum):
    """PlaybackMetricCreatePlayerMode class."""

    P2P_MEDIA_LOADER = "p2p-media-loader"
    WEB_VIDEO = "web-video"

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.value)
