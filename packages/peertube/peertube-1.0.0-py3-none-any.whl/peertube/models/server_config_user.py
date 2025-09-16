from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="ServerConfigUser")


@_attrs_define
class ServerConfigUser:
    """Attributes:
    video_quota (Union[Unset, int]): In bytes Example: 16810141515.
    video_quota_daily (Union[Unset, int]): In bytes Example: 1681014151.
    """

    video_quota: Unset | int = UNSET
    video_quota_daily: Unset | int = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        video_quota = self.video_quota

        video_quota_daily = self.video_quota_daily

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if video_quota is not UNSET:
            field_dict["videoQuota"] = video_quota
        if video_quota_daily is not UNSET:
            field_dict["videoQuotaDaily"] = video_quota_daily

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        video_quota = d.pop("videoQuota", UNSET)

        video_quota_daily = d.pop("videoQuotaDaily", UNSET)

        server_config_user = cls(
            video_quota=video_quota,
            video_quota_daily=video_quota_daily,
        )

        server_config_user.additional_properties = d
        return server_config_user

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
