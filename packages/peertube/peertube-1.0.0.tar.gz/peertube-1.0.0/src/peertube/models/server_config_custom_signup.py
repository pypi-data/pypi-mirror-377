from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="ServerConfigCustomSignup")


@_attrs_define
class ServerConfigCustomSignup:
    """Attributes:
    enabled (Union[Unset, bool]):
    limit (Union[Unset, int]):
    requires_email_verification (Union[Unset, bool]):
    """

    enabled: Unset | bool = UNSET
    limit: Unset | int = UNSET
    requires_email_verification: Unset | bool = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        enabled = self.enabled

        limit = self.limit

        requires_email_verification = self.requires_email_verification

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if limit is not UNSET:
            field_dict["limit"] = limit
        if requires_email_verification is not UNSET:
            field_dict["requiresEmailVerification"] = requires_email_verification

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        limit = d.pop("limit", UNSET)

        requires_email_verification = d.pop("requiresEmailVerification", UNSET)

        server_config_custom_signup = cls(
            enabled=enabled,
            limit=limit,
            requires_email_verification=requires_email_verification,
        )

        server_config_custom_signup.additional_properties = d
        return server_config_custom_signup

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
