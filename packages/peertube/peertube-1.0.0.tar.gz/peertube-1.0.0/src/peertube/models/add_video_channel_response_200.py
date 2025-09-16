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
    from peertube.models.add_video_channel_response_200_video_channel import (
        AddVideoChannelResponse200VideoChannel,
    )


T = TypeVar("T", bound="AddVideoChannelResponse200")


@_attrs_define
class AddVideoChannelResponse200:
    """Attributes:
    video_channel (Union[Unset, AddVideoChannelResponse200VideoChannel]):
    """

    video_channel: Union[Unset, "AddVideoChannelResponse200VideoChannel"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        video_channel: Unset | dict[str, Any] = UNSET
        if not isinstance(self.video_channel, Unset):
            video_channel = self.video_channel.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if video_channel is not UNSET:
            field_dict["videoChannel"] = video_channel

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.add_video_channel_response_200_video_channel import (
            AddVideoChannelResponse200VideoChannel,
        )

        d = dict(src_dict)
        _video_channel = d.pop("videoChannel", UNSET)
        video_channel: Unset | AddVideoChannelResponse200VideoChannel
        if isinstance(_video_channel, Unset):
            video_channel = UNSET
        else:
            video_channel = AddVideoChannelResponse200VideoChannel.from_dict(
                _video_channel
            )

        add_video_channel_response_200 = cls(
            video_channel=video_channel,
        )

        add_video_channel_response_200.additional_properties = d
        return add_video_channel_response_200

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
