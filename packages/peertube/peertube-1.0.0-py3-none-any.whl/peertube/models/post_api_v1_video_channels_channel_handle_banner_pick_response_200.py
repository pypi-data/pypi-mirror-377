from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.actor_image import ActorImage


T = TypeVar("T", bound="PostApiV1VideoChannelsChannelHandleBannerPickResponse200")


@_attrs_define
class PostApiV1VideoChannelsChannelHandleBannerPickResponse200:
    """Attributes:
    banners (Union[Unset, list['ActorImage']]):
    """

    banners: Unset | list["ActorImage"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        banners: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.banners, Unset):
            banners = []
            for banners_item_data in self.banners:
                banners_item = banners_item_data.to_dict()
                banners.append(banners_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if banners is not UNSET:
            field_dict["banners"] = banners

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.actor_image import ActorImage

        d = dict(src_dict)
        banners = []
        _banners = d.pop("banners", UNSET)
        for banners_item_data in _banners or []:
            banners_item = ActorImage.from_dict(banners_item_data)

            banners.append(banners_item)

        post_api_v1_video_channels_channel_handle_banner_pick_response_200 = cls(
            banners=banners,
        )

        post_api_v1_video_channels_channel_handle_banner_pick_response_200.additional_properties = d
        return post_api_v1_video_channels_channel_handle_banner_pick_response_200

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
