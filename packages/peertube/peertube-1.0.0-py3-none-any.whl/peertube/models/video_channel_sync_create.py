from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="VideoChannelSyncCreate")


@_attrs_define
class VideoChannelSyncCreate:
    """Attributes:
    external_channel_url (Union[Unset, str]):  Example: https://youtube.com/c/UC_myfancychannel.
    video_channel_id (Union[Unset, int]):  Example: 42.
    """

    external_channel_url: Unset | str = UNSET
    video_channel_id: Unset | int = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        external_channel_url = self.external_channel_url

        video_channel_id = self.video_channel_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if external_channel_url is not UNSET:
            field_dict["externalChannelUrl"] = external_channel_url
        if video_channel_id is not UNSET:
            field_dict["videoChannelId"] = video_channel_id

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        d = dict(src_dict)
        external_channel_url = d.pop("externalChannelUrl", UNSET)

        video_channel_id = d.pop("videoChannelId", UNSET)

        video_channel_sync_create = cls(
            external_channel_url=external_channel_url,
            video_channel_id=video_channel_id,
        )

        video_channel_sync_create.additional_properties = d
        return video_channel_sync_create

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
