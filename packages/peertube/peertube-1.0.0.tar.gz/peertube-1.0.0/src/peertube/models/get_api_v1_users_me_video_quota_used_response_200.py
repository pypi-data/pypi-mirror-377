from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="GetApiV1UsersMeVideoQuotaUsedResponse200")


@_attrs_define
class GetApiV1UsersMeVideoQuotaUsedResponse200:
    """Attributes:
    video_quota_used (Union[Unset, float]): The user video quota used so far in bytes Example: 16810141515.
    video_quota_used_daily (Union[Unset, float]): The user video quota used today in bytes Example: 1681014151.
    """

    video_quota_used: Unset | float = UNSET
    video_quota_used_daily: Unset | float = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        video_quota_used = self.video_quota_used

        video_quota_used_daily = self.video_quota_used_daily

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if video_quota_used is not UNSET:
            field_dict["videoQuotaUsed"] = video_quota_used
        if video_quota_used_daily is not UNSET:
            field_dict["videoQuotaUsedDaily"] = video_quota_used_daily

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        video_quota_used = d.pop("videoQuotaUsed", UNSET)

        video_quota_used_daily = d.pop("videoQuotaUsedDaily", UNSET)

        get_api_v1_users_me_video_quota_used_response_200 = cls(
            video_quota_used=video_quota_used,
            video_quota_used_daily=video_quota_used_daily,
        )

        get_api_v1_users_me_video_quota_used_response_200.additional_properties = d
        return get_api_v1_users_me_video_quota_used_response_200

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
