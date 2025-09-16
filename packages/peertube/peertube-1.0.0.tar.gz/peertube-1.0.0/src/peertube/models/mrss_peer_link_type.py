from enum import Enum


class MRSSPeerLinkType(str, Enum):
    """MRSSPeerLinkType enumeration."""

    APPLICATIONX_BITTORRENT = "application/x-bittorrent"

    def __str__(self) -> str:
        return str(self.value)
