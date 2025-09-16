from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.server_config_custom_auto_blacklist_videos import (
        ServerConfigCustomAutoBlacklistVideos,
    )


T = TypeVar("T", bound="ServerConfigCustomAutoBlacklist")


@_attrs_define
class ServerConfigCustomAutoBlacklist:
    """Attributes:
    videos (Union[Unset, ServerConfigCustomAutoBlacklistVideos]):
    """

    videos: Union[Unset, "ServerConfigCustomAutoBlacklistVideos"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        videos: Unset | dict[str, Any] = UNSET
        if not isinstance(self.videos, Unset):
            videos = self.videos.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if videos is not UNSET:
            field_dict["videos"] = videos

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_custom_auto_blacklist_videos import (
            ServerConfigCustomAutoBlacklistVideos,
        )

        d = dict(src_dict)
        _videos = d.pop("videos", UNSET)
        videos: Unset | ServerConfigCustomAutoBlacklistVideos
        if isinstance(_videos, Unset):
            videos = UNSET
        else:
            videos = ServerConfigCustomAutoBlacklistVideos.from_dict(_videos)

        server_config_custom_auto_blacklist = cls(
            videos=videos,
        )

        server_config_custom_auto_blacklist.additional_properties = d
        return server_config_custom_auto_blacklist

    @property
    def additional_keys(self) -> list[str]:
        """Get additional property keys."""
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
