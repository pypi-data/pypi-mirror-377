from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="ServerConfigSearchRemoteUri")


@_attrs_define
class ServerConfigSearchRemoteUri:
    """Attributes:
    users (Union[Unset, bool]):
    anonymous (Union[Unset, bool]):
    """

    users: Unset | bool = UNSET
    anonymous: Unset | bool = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        users = self.users

        anonymous = self.anonymous

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if users is not UNSET:
            field_dict["users"] = users
        if anonymous is not UNSET:
            field_dict["anonymous"] = anonymous

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        users = d.pop("users", UNSET)

        anonymous = d.pop("anonymous", UNSET)

        server_config_search_remote_uri = cls(
            users=users,
            anonymous=anonymous,
        )

        server_config_search_remote_uri.additional_properties = d
        return server_config_search_remote_uri

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
