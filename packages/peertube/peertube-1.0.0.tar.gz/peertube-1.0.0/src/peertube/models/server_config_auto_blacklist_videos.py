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
    from peertube.models.server_config_auto_blacklist_videos_of_users import (
        ServerConfigAutoBlacklistVideosOfUsers,
    )


T = TypeVar("T", bound="ServerConfigAutoBlacklistVideos")


@_attrs_define
class ServerConfigAutoBlacklistVideos:
    """Attributes:
    of_users (Union[Unset, ServerConfigAutoBlacklistVideosOfUsers]):
    """

    of_users: Union[Unset, "ServerConfigAutoBlacklistVideosOfUsers"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        of_users: Unset | dict[str, Any] = UNSET
        if not isinstance(self.of_users, Unset):
            of_users = self.of_users.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if of_users is not UNSET:
            field_dict["ofUsers"] = of_users

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_auto_blacklist_videos_of_users import (
            ServerConfigAutoBlacklistVideosOfUsers,
        )

        d = dict(src_dict)
        _of_users = d.pop("ofUsers", UNSET)
        of_users: Unset | ServerConfigAutoBlacklistVideosOfUsers
        if isinstance(_of_users, Unset):
            of_users = UNSET
        else:
            of_users = ServerConfigAutoBlacklistVideosOfUsers.from_dict(_of_users)

        server_config_auto_blacklist_videos = cls(
            of_users=of_users,
        )

        server_config_auto_blacklist_videos.additional_properties = d
        return server_config_auto_blacklist_videos

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
