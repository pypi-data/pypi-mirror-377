from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="ServerConfigExportUsers")


@_attrs_define
class ServerConfigExportUsers:
    """Attributes:
    enabled (Union[Unset, bool]):
    export_expiration (Union[Unset, float]): In milliseconds
    max_user_video_quota (Union[Unset, float]): In bytes
    """

    enabled: Unset | bool = UNSET
    export_expiration: Unset | float = UNSET
    max_user_video_quota: Unset | float = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        enabled = self.enabled

        export_expiration = self.export_expiration

        max_user_video_quota = self.max_user_video_quota

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if export_expiration is not UNSET:
            field_dict["exportExpiration"] = export_expiration
        if max_user_video_quota is not UNSET:
            field_dict["maxUserVideoQuota"] = max_user_video_quota

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        export_expiration = d.pop("exportExpiration", UNSET)

        max_user_video_quota = d.pop("maxUserVideoQuota", UNSET)

        server_config_export_users = cls(
            enabled=enabled,
            export_expiration=export_expiration,
            max_user_video_quota=max_user_video_quota,
        )

        server_config_export_users.additional_properties = d
        return server_config_export_users

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
