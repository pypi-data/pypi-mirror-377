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
    from peertube.models.server_config_custom_import_video_channel_synchronization import (
        ServerConfigCustomImportVideoChannelSynchronization,
    )
    from peertube.models.server_config_custom_import_videos import (
        ServerConfigCustomImportVideos,
    )


T = TypeVar("T", bound="ServerConfigCustomImport")


@_attrs_define
class ServerConfigCustomImport:
    """Attributes:
    videos (Union[Unset, ServerConfigCustomImportVideos]):
    video_channel_synchronization (Union[Unset, ServerConfigCustomImportVideoChannelSynchronization]):
    """

    videos: Union[Unset, "ServerConfigCustomImportVideos"] = UNSET
    video_channel_synchronization: Union[
        Unset, "ServerConfigCustomImportVideoChannelSynchronization"
    ] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        videos: Unset | dict[str, Any] = UNSET
        if not isinstance(self.videos, Unset):
            videos = self.videos.to_dict()

        video_channel_synchronization: Unset | dict[str, Any] = UNSET
        if not isinstance(self.video_channel_synchronization, Unset):
            video_channel_synchronization = self.video_channel_synchronization.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if videos is not UNSET:
            field_dict["videos"] = videos
        if video_channel_synchronization is not UNSET:
            field_dict["video_channel_synchronization"] = video_channel_synchronization

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_custom_import_video_channel_synchronization import (
            ServerConfigCustomImportVideoChannelSynchronization,
        )
        from peertube.models.server_config_custom_import_videos import (
            ServerConfigCustomImportVideos,
        )

        d = dict(src_dict)
        _videos = d.pop("videos", UNSET)
        videos: Unset | ServerConfigCustomImportVideos
        if isinstance(_videos, Unset):
            videos = UNSET
        else:
            videos = ServerConfigCustomImportVideos.from_dict(_videos)

        _video_channel_synchronization = d.pop("video_channel_synchronization", UNSET)
        video_channel_synchronization: (
            Unset | ServerConfigCustomImportVideoChannelSynchronization
        )
        if isinstance(_video_channel_synchronization, Unset):
            video_channel_synchronization = UNSET
        else:
            video_channel_synchronization = (
                ServerConfigCustomImportVideoChannelSynchronization.from_dict(
                    _video_channel_synchronization
                )
            )

        server_config_custom_import = cls(
            videos=videos,
            video_channel_synchronization=video_channel_synchronization,
        )

        server_config_custom_import.additional_properties = d
        return server_config_custom_import

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
