from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1ServerFollowingBody")


@_attrs_define
class PostApiV1ServerFollowingBody:
    """Attributes:
    hosts (Union[Unset, list[str]]):
    handles (Union[Unset, list[str]]):
    """

    hosts: Unset | list[str] = UNSET
    handles: Unset | list[str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        hosts: Unset | list[str] = UNSET
        if not isinstance(self.hosts, Unset):
            hosts = self.hosts

        handles: Unset | list[str] = UNSET
        if not isinstance(self.handles, Unset):
            handles = self.handles

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hosts is not UNSET:
            field_dict["hosts"] = hosts
        if handles is not UNSET:
            field_dict["handles"] = handles

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        d = dict(src_dict)
        hosts = cast("list[str]", d.pop("hosts", UNSET))

        handles = cast("list[str]", d.pop("handles", UNSET))

        post_api_v1_server_following_body = cls(
            hosts=hosts,
            handles=handles,
        )

        post_api_v1_server_following_body.additional_properties = d
        return post_api_v1_server_following_body

    @property
    def additional_keys(self) -> list[str]:
        """Get additional keys."""
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
