from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="VideoChannelEdit")


@_attrs_define
class VideoChannelEdit:
    """Attributes:
    display_name (Union[Unset, Any]): Channel display name
    description (Union[Unset, Any]): Channel description
    support (Union[Unset, Any]): How to support/fund the channel
    """

    display_name: Unset | Any = UNSET
    description: Unset | Any = UNSET
    support: Unset | Any = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        display_name = self.display_name

        description = self.description

        support = self.support

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if description is not UNSET:
            field_dict["description"] = description
        if support is not UNSET:
            field_dict["support"] = support

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        display_name = d.pop("displayName", UNSET)

        description = d.pop("description", UNSET)

        support = d.pop("support", UNSET)

        video_channel_edit = cls(
            display_name=display_name,
            description=description,
            support=support,
        )

        video_channel_edit.additional_properties = d
        return video_channel_edit

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
