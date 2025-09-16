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
    from peertube.models.server_config_import_users import ServerConfigImportUsers
    from peertube.models.server_config_import_video_channel_synchronization import (
        ServerConfigImportVideoChannelSynchronization,
    )
    from peertube.models.server_config_import_videos import ServerConfigImportVideos


T = TypeVar("T", bound="ServerConfigImport")


@_attrs_define
class ServerConfigImport:
    """Attributes:
    videos (Union[Unset, ServerConfigImportVideos]):
    video_channel_synchronization (Union[Unset, ServerConfigImportVideoChannelSynchronization]):
    users (Union[Unset, ServerConfigImportUsers]):
    """

    videos: Union[Unset, "ServerConfigImportVideos"] = UNSET
    video_channel_synchronization: Union[
        Unset, "ServerConfigImportVideoChannelSynchronization"
    ] = UNSET
    users: Union[Unset, "ServerConfigImportUsers"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        videos: Unset | dict[str, Any] = UNSET
        if not isinstance(self.videos, Unset):
            videos = self.videos.to_dict()

        video_channel_synchronization: Unset | dict[str, Any] = UNSET
        if not isinstance(self.video_channel_synchronization, Unset):
            video_channel_synchronization = self.video_channel_synchronization.to_dict()

        users: Unset | dict[str, Any] = UNSET
        if not isinstance(self.users, Unset):
            users = self.users.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if videos is not UNSET:
            field_dict["videos"] = videos
        if video_channel_synchronization is not UNSET:
            field_dict["videoChannelSynchronization"] = video_channel_synchronization
        if users is not UNSET:
            field_dict["users"] = users

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_import_users import ServerConfigImportUsers
        from peertube.models.server_config_import_video_channel_synchronization import (
            ServerConfigImportVideoChannelSynchronization,
        )
        from peertube.models.server_config_import_videos import ServerConfigImportVideos

        d = dict(src_dict)
        _videos = d.pop("videos", UNSET)
        videos: Unset | ServerConfigImportVideos
        if isinstance(_videos, Unset):
            videos = UNSET
        else:
            videos = ServerConfigImportVideos.from_dict(_videos)

        _video_channel_synchronization = d.pop("videoChannelSynchronization", UNSET)
        video_channel_synchronization: (
            Unset | ServerConfigImportVideoChannelSynchronization
        )
        if isinstance(_video_channel_synchronization, Unset):
            video_channel_synchronization = UNSET
        else:
            video_channel_synchronization = (
                ServerConfigImportVideoChannelSynchronization.from_dict(
                    _video_channel_synchronization
                )
            )

        _users = d.pop("users", UNSET)
        users: Unset | ServerConfigImportUsers
        if isinstance(_users, Unset):
            users = UNSET
        else:
            users = ServerConfigImportUsers.from_dict(_users)

        server_config_import = cls(
            videos=videos,
            video_channel_synchronization=video_channel_synchronization,
            users=users,
        )

        server_config_import.additional_properties = d
        return server_config_import

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
